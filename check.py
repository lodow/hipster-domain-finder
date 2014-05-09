#!/usr/bin/python
# command -> ./check.py <gandi API key>

#pp.pprint(result) # your code here ...

import argparse
import os
from pymongo import MongoClient
from time import sleep
import xmlrpclib
import subprocess
import pprint
#from pprint import pprint
from SOAPpy import WSDL


db = MongoClient('localhost', 27017).hipsterdomainfinderfr

soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')
session = soap.login("XXXXXX", "XXXXX","fr", 0);
vowels = ('a', 'e', 'i', 'o', 'u', 'y')
domains = []
#tlds = gandi.domain.tld.list(key)
#for i, tld in enumerate(tlds):
#    tlds[i] = tld['name']
#tlds.remove('za') # .za has no whois server, gandi hasn't worked around it
#tlds.remove('ki') # gandi always returns "available" for .ki even when not
#tlds.append('ly') # must manually query .ly (plz gandi)

tlds = []

tlds.append('fr')
tlds.append('com')
tlds.append('eu')
tlds.append('net')
tlds.append('be')
tlds.append('org')
tlds.append('info')
tlds.append('biz')
tlds.append('tel')
tlds.append('pro')
tlds.append('tv')
tlds.append('me')
tlds.append('mobi')
tlds.append('name')
tlds.append('jobs')
tlds.append('travel')
tlds.append('xxx')
tlds.append('pl')
tlds.append('es')
tlds.append('de')
tlds.append('ch')
tlds.append('it')
tlds.append('at')
tlds.append('lu')
tlds.append('nl')
tlds.append('cz')
tlds.append('li')
tlds.append('cat')
tlds.append('pt')
tlds.append('se')
tlds.append('im')
tlds.append('lt')
tlds.append('lv')
tlds.append('fi')
tlds.append('ie')
tlds.append('ro')
tlds.append('dk')
tlds.append('hr')
tlds.append('cc')
tlds.append('us')
tlds.append('fm')
tlds.append('tw')
tlds.append('cx')
tlds.append('mu')
tlds.append('nu')
tlds.append('asia')
tlds.append('tl')
tlds.append('ht')
tlds.append('am')
tlds.append('sn')
tlds.append('gs')
tlds.append('re')
tlds.append('pm')
tlds.append('wf')
tlds.append('tf')
tlds.append('yt')
tlds.append('la')
tlds.append('ag')
tlds.append('bz')
tlds.append('hn')
tlds.append('lc')
tlds.append('mn')
tlds.append('sc')
tlds.append('vc')
tlds.append('co')
tlds.append('in')
tlds.append('cm')
tlds.append('ms')
tlds.append('mg')
tlds.append('af')
tlds.append('ki')
tlds.append('nf')
tlds.append('hk')
tlds.append('gy')
tlds.append('so')
tlds.append('sh')
tlds.append('io')
tlds.append('ac')
tlds.append('ly')

tlds = tuple(tlds)

fn = os.path.join(os.path.dirname(__file__), 'clean_fr.txt')
with open(fn) as dictionary:
    for line in dictionary:
        word = line.strip(' ')
        word = word.strip('\'')
        word = word.strip('\n')
        chars = list(word)
        if len(word) > 4:
            if word.endswith(tlds):
                end = next((suf for suf in tlds if word.endswith(suf)), None)
                if len(word) > len(end):
                    chars.insert(-len(end), '.')
                    domains.append(''.join(chars))
            elif ''.join(chars.pop(-1)).endswith(tlds):
                word = ''.join(chars.pop(-1))
                end = next((suf for suf in tlds if word.endswith(suf)), None)
                if len(word) > len(end):
                    chars.insert(-len(end), '.')
                    domains.append(''.join(chars))

available = []
hold = [] # domains to check later due to rate limit

def move_to_hold(end):
    global domains
    global hold

    before = len(domains)
    for name in list(domains):
        if name.endswith(end):
            hold.append(name)
            domains.remove(name)
    print('Removed ' + str(before - len(domains)) + ' domains')

def check():
    global domains
    global hold
    global session

    while len(domains):
        name = domains[0]
#        if name.endswith('ly'):
        whois = subprocess.check_output('whois '+ name +'; exit 0', shell=True)
        if whois.find('found') != -1:
            print('Adding -> ' + name)
            db.domains.update({'name': name}, {
                'name': name,
                'tld': 'ly',
                'length': len(name)
            }, True)
        elif whois.find('Ce TLD n\'a pas de serveur whois') != -1:
            try :
                result = soap.domainCheck(session, name)
            finally :
                print('Sleeping..... ZZzzz')
                sleep(60 * 60)
                print('Going again!')
                result = soap.domainCheck(session, name)
            if result[0][0][1] == True:
                print('Adding -> ' + name)
                db.domains.update({'name': name}, {
                    'name': name,
                    'tld': name.split('.')[1],
                    'length': len(name)
                }, True)
            else:
                print('Removing -> ' + name)
                print('    > For reason: ' + str(result[0][1]))
                db.domains.remove({'name': name})
        else:
            print('Removing -> ' + name)
            print('    > For reason: ' + 'NOT "available" whois')
            print('        > ' + whois[:30])
            db.domains.remove({'name': name})
        domains.remove(name)
        print('')
        print('domains: ' + str(len(domains)))
        print('hold: ' + str(len(hold)))


    if len(hold):
        domains = list(hold)
        hold = []
        check()

check()
soap.logout(session)
