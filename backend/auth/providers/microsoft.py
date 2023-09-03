import json

import msal
import requests

from backend import settings
from backend.auth.providers.base import OauthProvider
from backend.disciplines.tasks import send_discord_message
from backend.users.models import MicrosoftUser, Clazz, Grade


class MicrosoftOauthProvider(OauthProvider):
    name = "microsoft"
    oauth_user_model = MicrosoftUser
    user_property = "microsoft_user"

    def get_msal_app(self, cache=None):
        # Initialize the MSAL confidential client
        auth_app = msal.ConfidentialClientApplication(
            settings.MICROSOFT_APP_ID,
            authority=settings.MICROSOFT_AUTHORITY,
            client_credential=settings.MICROSOFT_APP_SECRET,
            token_cache=cache)
        return auth_app

    def start_flow(self, request, callback_url):
        auth_app = self.get_msal_app()
        return auth_app.initiate_auth_code_flow(
            settings.MICROSOFT_SCOPES,
            redirect_uri=callback_url)

    def get_service_url(self, request, flow, callback_url):
        return flow['auth_uri']

    def format_callback_query(self, request):
        return ""

    def __get_oauth_user(self, user):
        id = user['id']

        if not MicrosoftUser.objects.filter(id=id).exists():
            MicrosoftUser.objects.create(
                id=id,
                mail=user['mail'],
                display_name=user['displayName'],
                given_name=user['givenName'],
                surname=user['surname'],
                job_title=user['jobTitle'],
                office_location=user['officeLocation'],
                department=user['department'],
            )
        else:
            # check if all information is up to date and update if necessary
            msft_user = MicrosoftUser.objects.get(id=id)
            changed = False
            for key in ['mail', 'display_Name', 'given_Name', 'surname', 'job_Title', 'office_Location', 'department']:
                key1, key2 = key.lower(), key.replace('_', '')
                if getattr(msft_user, key1) != user[key2]:
                    setattr(msft_user, key1, user[key2])
                    changed = True
            if changed:
                msft_user.save()

        return MicrosoftUser.objects.get(id=id)

    def get_oauth_user(self, request, flow):
        auth_app = self.get_msal_app()

        result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)

        user = requests.get('https://graph.microsoft.com/v1.0/me',
                            headers={'Authorization': f"Bearer {result['access_token']}"},
                            params={
                                '$select': 'displayName,jobTitle,mail,givenName,surname,id,officeLocation,department,'
                                           'userPrincipalName'}).json()

        return self.__get_oauth_user(user)

    def get_verification_oauth_user(self, request):
        data = json.loads(request.body.decode('utf-8'))
        if 'access_token' not in data:
            raise Exception("No access token in POST data")

        user = requests.get('https://graph.microsoft.com/v1.0/me',
                            headers={'Authorization': f"Bearer {data['access_token']}"},
                            params={
                                '$select': 'displayName,jobTitle,mail,givenName,surname,id,officeLocation,department,'
                                           'userPrincipalName'}).json()

        try:
            for key in ['displayName', 'jobTitle', 'mail', 'givenName', 'surname', 'id', 'officeLocation', 'department',
                        'userPrincipalName']:
                if key not in user:
                    raise Exception(f"POSSIBLE FRAUD: Key {key} not in user data")

                if user[key] != data['user'][key]:
                    raise Exception(f"POSSIBLE FRAUD: Key {key} does not match")
        except Exception as e:
            if 'POSSIBLE FRAUD' in str(e):
                send_discord_message(f"<@528364834836709376> **Possible login fraud detected**\n"
                                     f"Real user: {user['id']}\n"
                                     f"Imitated user: {data['user']['id']}\n"
                                     f"More details can be found in the logs.")
                print(f"--- POSSIBLE LOGIN FRAUD ---\n"
                      f"Real user:\n"
                        f" - ID: {user['id']}\n"
                        f" - Name: {user['displayName']}\n"
                        f" - Email: {user['mail']}\n"
                      f"Imitated user:\n"
                        f" - ID: {data['user']['id']}\n"
                        f" - Name: {data['user']['displayName']}\n"
                        f" - Email: {data['user']['mail']}\n"
                      f"Request:\n"
                        f" - IP: {request.META['REMOTE_ADDR']}\n"
                      f"--------- RAW DATA ---------\n"
                        f"Real user: {json.dumps(user)}\n"
                        f"Imitated user: {json.dumps(data['user'])}\n"
                        f"Request: {str(request)}\n"
                      f"--------- EXCEPTION --------\n"
                        f"{str(e)}\n"
                      f"----------------------------\n")
            raise e

        return self.__get_oauth_user(user)

    def get_user_props(self, request, flow, oauth_user=None):
        user_clazz = self.process_clazz(oauth_user)
        return {

            "microsoft_user": oauth_user,
            "clazz": user_clazz,

            "username": f"{oauth_user.given_name} {oauth_user.surname}",
            "email": oauth_user.mail,

            "first_name": oauth_user.given_name,
            "last_name": oauth_user.surname,

            "is_active": True,
            "is_staff": user_clazz.grade.is_organiser
        }

    def get_verification_user_props(self, request, oauth_user=None):
        return self.get_user_props(request, None, oauth_user)

    def process_clazz(self, oauth_user):
        if oauth_user.get_clazz() is not None:
            return oauth_user.get_clazz()
        else:
            if oauth_user.department == 'alumni':
                return Clazz.objects.create(
                    name='Alumni',
                    grade=Grade.objects.get(name='Alumni'),
                    is_fake=True,
                    microsoft_department='alumni'
                )
            elif oauth_user.department == 'zamestnanci':
                return Clazz.objects.create(
                    name='Učitelia',
                    grade=Grade.objects.get(name='Učitelia'),
                    is_fake=True,
                    microsoft_department='zamestnanci'
                )
            else:
                if '.' in oauth_user.department:
                    year, clazz = oauth_user.department.split('.')
                    return Clazz.objects.create(
                        name=year + ". " + clazz,
                        grade=Grade.objects.get(name="3. Stupeň"),
                        is_fake=False,
                        microsoft_department=oauth_user.department
                    )
                else:
                    clazz = oauth_user.department

                    grade = Grade.objects.get(name="3. Stupeň")
                    if clazz[:-1] in ['Prima', 'Sekunda', 'Tercia', 'Kvarta']:
                        grade = Grade.objects.get(name="2. Stupeň")

                    if clazz[-1] == 'A' or clazz[-1] == 'B':
                        clazz = clazz[:-1] + ' ' + clazz[-1]

                    return Clazz.objects.create(
                        name=clazz,
                        grade=grade,
                        is_fake=False,
                        microsoft_department=oauth_user.department
                    )

    def get_check_params(self, request, user=None, oauth_user=None, user_props=None):
        if oauth_user is not None:
            return {
                'microsoft_department': oauth_user.department,
                **super().get_check_params(request, user, oauth_user, user_props)
            }
        elif user is not None and user.microsoft_user is not None:
            return {
                'microsoft_department': user.microsoft_user.department,
                **super().get_check_params(request, user, oauth_user, user_props)
            }
        else:
            return super().get_check_params(request, user, oauth_user, user_props)
