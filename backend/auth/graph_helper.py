import requests

graph_url = 'https://graph.microsoft.com/v1.0'


def get_user(token):
    # Send GET to /me
    user = requests.get('{0}/me'.format(graph_url),
                        headers={'Authorization': 'Bearer {0}'.format(token)},
                        params={
                            '$select': 'displayName,jobTitle,mail,givenName,surname,id,officeLocation,department,'
                                       'userPrincipalName'})
    return user.json()
