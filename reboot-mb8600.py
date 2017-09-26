#!/usr/bin/python

'''
A hacky script to reboot the Motorola MB8600 modem.
'''

import urllib, urllib2, sys
from bs4 import BeautifulSoup

MODEM_IP = '192.168.100.1'
USERNAME = 'admin'
PASSWORD = 'motorola'
ENCODED_PASSWORD = 'bW90b3JvbGE' # get from login URL from web UI.

def login(modem) :
    '''
    The modem seems to just be in a global "logged in" state once the password
    is sent -- no cookies are set.
    '''
    # the password is encoded with some simple function in JS. It is a
    # symmetric encoding of some form, so the encoding is always the same. This
    # is the encoding of the default password 'motorola'. Note that the ordering
    # of the arguments matters, and so does the trailing '=&' that we tack on
    # to the end of the URL.
    args = [
        ('loginUsername', USERNAME),
        ('loginPassword', ENCODED_PASSWORD)
    ]
    encodedArgs = urllib.urlencode(args)
    url = 'http://%(modem)s/login_auth.html?%(encodedArgs)s=&' % locals()

    # This will respond with a 200 return code with a HTML body claiming that
    # there was a 400 error if login was successful, or an actual 400 error if
    # the login was not successful.
    try :
        urllib2.urlopen(url).read()
    except urllib2.HTTPError, e :
        print >> sys.stderr, "400 error returned from modem. Check the password"
        raise e

def getSession(modem) :
    # the session key is included as a hidden field on the form with the reboot
    # button. We use BeautifulSoup to extract it.
    req = urllib2.Request('http://%(modem)s/MotoSecurity.html' % locals())
    html = urllib2.urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    sessionField = soup.find(attrs={'name' : 'sessionKey'})
    return str(sessionField.attrs['value'])

def reboot(modem, session) :
    # reconstruct the reboot request and send it here to start the reboot.
    argDict = [
        ('MotoUsername', USERNAME),
        ('MotoCurPassword', PASSWORD),
        ('MotoNewUsername', USERNAME),
        ('MotoNewPassword', PASSWORD),
        ('MotoRepPassword', PASSWORD),
        ('MotoSecurityAction', '1'),
        ('sessionKey', session)
    ]
    url = 'http://%(modem)s/goform/MotoSecurity' % locals()
    req = urllib2.Request(url, urllib.urlencode(argDict))
    urllib2.urlopen(req).read()

    # the response from the reboot request instructs us to visit this page, so
    # we do a fetch against it here. Otherwise the modem seems to not reboot.
    urllib2.urlopen('http://%(modem)s/rebootinfo.html' % locals()).read()

def main() :
    login(MODEM_IP)
    session = getSession(MODEM_IP)
    reboot(MODEM_IP, session)

if __name__ == '__main__' :
    main()

