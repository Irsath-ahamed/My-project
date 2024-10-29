# Initial version sometime in 2016? (JMike)
# A couple fixes for Python 3, June 2019 (JMike)

import getpass
import os
import string

def get_auth0_credentials( ):
    try:
        username = os.environ['USER_AUTH0']
    except KeyError:
        print('Environment variable USER_AUTH0 not set.')
        username = input("Your Auth0 username (don't forget the @cimpress.com part): ")
        if username.find('@') == -1:
            username = '%s@cimpress.com' % username
    try:
        password = os.environ['PW']
    except KeyError:
        print('Environment variable PW not set.')
        password = getpass.getpass('Your Auth0 password:')

    return (username, password)
