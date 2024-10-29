# handle auth tokens for a service
# Initial version sometime in 2016? (JMike)
# upgrade to Python 3, May 2019 (JMike)

import os
import requests
import time
from . import get_auth0_credentials

# this client is a special one provided by API Management that allows users to log in with
# their own username and password rather than the client secret

(username, password) = get_auth0_credentials.get_auth0_credentials( )

def get_v2_auth_token( ):

    tok = ''

    if os.path.isdir(os.environ['TMP']):
        token_dir = os.environ['TMP']
    elif os.path.isdir(os.environ['TEMP']):
        token_dir = os.environ['TEMP']
    else:
        token_dir = '.'
    
    token_file = '%s/universal_v2_auth_token' % token_dir

    if os.path.isfile( token_file ):
        if time.time() - os.path.getmtime( token_file )  < 30000:
            print('using existing v2 auth token %s' % token_file)
            tok = open( token_file ).read()
    if tok == '':
        print('generating new file %s' % token_file)
        h = {'Content-Type': 'application/json'}
        j = {'grant_type': 'http://auth0.com/oauth/grant-type/password-realm',
             'username': username,
             'password': password,
             'audience': 'https://api.cimpress.io/',
             'scope': 'openid',
             'client_id': 'ST0wwOc0RavK6P6hhAPZ9Oc2XFD2dGUF',
             # the above is a special API Management client that takes username/password
             'realm': 'cimpresscom-native-waad'
        }
        r = requests.post('https://cimpress.auth0.com/oauth/token', json=j, headers=h)
        if r.status_code != 200:
            print('ERROR: %s on auth0/oauth/token call' % r.status_code)
            print('$$$ auth0 response:\n')
            print(r.text)
            exit(-1)
        else:
            # print('Auth0 response: %s' % r.json())
            if os.path.exists( token_file ):
                os.remove( token_file )
            tok = r.json()["access_token"]
            open( token_file ,'w').write( tok )
    if tok != '':
        return tok
