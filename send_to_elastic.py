import json
import os
from pprint import pprint as pp
import requests
import re
import subprocess
import sys
import time

elastic_url = sys.argv[1]
job_url = sys.argv[2]

elasticsearch_bulk_cmd = 'curl -XPOST -H "Content-Type: application/json" \
    "%s" --data-binary @data.json' % elastic_url

m = re.match('^http.*/job/(?P<job>.*)/(?P<id>.*)/', job_url)
if m:
    job, build_id = m.groupdict().values()
else:
    raise "Wrong url %s" % job_url

commit = subprocess.check_output(['git', 'log', '--format="%H"', '-n 1'])
commit = commit.split('"')[1]

url = '%s/testReport/api/json' % job_url
response = requests.get(url, auth=('admin', 'admin'))
result = json.loads(response._content)

json_file = open('data.json','w')

for suite in result['suites']:
    for case in suite['cases']:
        line = '{'
        line += '"@timestamp": "%f", ' % (1000*time.time())
        line += '"job_name": "%s", ' % job
        line += '"revision": "%s", ' % commit
        line += '"build_id": "%s", ' % build_id
        line += '"class_name": "%s", ' % case['className']
        line += '"job_duration": "%s", ' % result['duration']
        line += '"test_duration": "%s", ' % case['duration']
        line += '"error_details": "%s", ' % case['errorDetails']
        line += '"error_stack_trace": "%s", ' % case['errorStackTrace']
        line += '"failed_since": "%s", ' % case['failedSince']
        line += '"test_name": "%s", ' % case['name']
        line += '"skipped": "%s", ' % case['skipped']
        line += '"skipped_message": "%s", ' % case['skippedMessage']
        line += '"status": "%s", ' % case['status']
        line += '"stderr": "%s", ' % case['stderr']
        line += '"stdout": "%s", ' % case['stdout']
        line += '"test_actions": "%s", ' % case['testActions']
        line += '"type": "%s", ' % "TODO"
        line += '"namespace": "%s", ' % "TODO"
        line += '"category": "%s", ' % "TODO"
        line += '"brand": "%s", ' % "TODO"
        line += '"tags": "%s", ' % "TODO"
        line += '"source": "%s"' % "TODO"
        line += "}\n"

        json_file.write('{ "index" : {} }\n')
        json_file.write(line)

json_file.close()
os.system(elasticsearch_bulk_cmd)
