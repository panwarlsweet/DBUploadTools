#! /usr/bin/env python
import os
import re
import sys
import subprocess
from optparse import OptionParser

parser = OptionParser()
parser.add_option('--db', metavar='F', type='string', action='store',
                  dest='db',
                  help='Input database')

parser.add_option('--era', metavar='F', type='string', action='store',
                  dest='era',
                  help='Input era')

parser.add_option('--production', metavar='F', action='store_true',
                  dest='production',
                  help='Upload to the production database instead of the test one')

parser.add_option('--prompt', metavar='F', action='store_true',
                  dest='prompt',
                  help='Tags are for prompt reconstruction')

parser.add_option('--offline', metavar='F', action='store_true',
                  dest='offline',
                  help='Tags are for offline reconstruction')

parser.add_option('--since', metavar='N', action='store', type=int,
                  dest='since',
                  help='Since IOV')

(options, args) = parser.parse_args()

if not options.prompt and not options.offline:
    raise Exception("You need to specify either --prompt or --offline")

if options.era is None:
    raise Exception("You must specify an era with --era")

database = options.db
if database is None:
    raise Exception("You must specify a database with --db")
    
if not os.path.exists(database):
    raise Exception("No database named %r found." % (database))

templateFile = "condb_template.txt"

if options.production :
    destinationDatabase = "oracle://cms_orcon_prod/CMS_CONDITIONS"
else :
    destinationDatabase = "oracle://cms_orcoff_prep/CMS_CONDITIONS"


template = None
with open(templateFile, 'r') as f:
    template = f.read(-1)

print '--------------- TEMPLATE -----------------'
print template

#******************   definitions  **********************************
ERA         = options.era
algsizetype = {'ak': [4, 8]}  # other options: ic, kt and any cone size
jettype = ['pf', 'pfchs', 'puppi']  # other options: calo

algsizetypeAK4 = {'ak': [4]}
algsizetypeAK8 = {'ak': [8]}
jettypeAK4 = ['pf', 'pfchs', 'puppi', 'calo', 'jpt']
jettypeAK8 = ['pf', 'pfchs', 'puppi']

ALGO_LIST = []
#for k, v in algsizetype.iteritems():
#    for s in v:
#        for j in jettype:
#            ALGO_LIST.append(str(k.upper()+str(s)+j.upper().replace("CHS","chs").replace("PUPPI","PFPuppi")))

for k, v in algsizetypeAK4.iteritems():
    for s in v:
        for j in jettypeAK4:
            ALGO_LIST.append(str(k.upper()+str(s)+j.upper().replace("CHS","chs").replace("PUPPI","PFPuppi").replace("CALO","Calo")))
for k, v in algsizetypeAK8.iteritems():
    for s in v:
        for j in jettypeAK8:
            ALGO_LIST.append(str(k.upper()+str(s)+j.upper().replace("CHS","chs").replace("PUPPI","PFPuppi")))

files = []

if not os.path.exists('templates'):
    os.makedirs('templates')

for algo in ALGO_LIST: #loop for jet algorithms

    t = template

    input_tag = "JetCorrectorParametersCollection_%s_%s" % (ERA, algo)
    dest_tag = input_tag if options.offline else "JetCorrectorParametersCollection_%s_v0_express" % algo
    since = str(options.since) if options.since else "null"

    t = t.replace('DEST_DATABASE', destinationDatabase)
    t = t.replace('INPUT_TAG', input_tag)
    t = t.replace('DEST_TAG', dest_tag)
    t = t.replace('SINCE', since)

    # Save the template
    local_template = os.path.join('templates', input_tag)
    with open(local_template + '.txt', 'w') as f:
        f.write(t)

    # Create a symlink of the database
    link = local_template + '.db'
    if os.path.lexists(link):
        os.remove(link)
    os.symlink(os.path.abspath(database), local_template + '.db')
    
    files.append(local_template + '.txt')
    
for f in files:
    args = ["./uploadConditions.py", f]
    subprocess.call(args)
