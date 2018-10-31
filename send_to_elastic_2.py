
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script re-feeds elastic-search from jenkins.
Example:

python send_to_elastic_2.py "Frontend/job/frontend-dashboard-timeseries" \
       frontend-dashboard-timeseries jenkins test frontend ""

"""

import datetime
import hashlib
import json
import os
import requests
import re
import subprocess
import sys
import time

from pprint import pprint as pp

jenkins_url = "https://jenkins-ci1.local.corvil.com/"
elastic_url = "http://elasticsearch.local.corvil.com:9200/_bulk"
cmd_send_to_elastic = 'curl -i -XPOST --user elastic:changeme -H "Content-Type: application/json"  "http://elasticsearch.local.corvil.com:9200/_bulk" --data-binary @"data.json"'

job_name, namespace, source, the_type, category, brand = sys.argv[1:]

def scape(text):
    text = text and text.replace('"', r'\"').replace('\n', r'\n').replace('\t', r'  ').replace('|', r' ') or ''
    return text

def send_to_elastic():
    result = os.system(cmd_send_to_elastic)

def process(build_id):

    print "\n\n####### Processing %s" % build_id

    try:
        # Get tests results
        url = '%s/job/%s/%s/testReport/api/json' % (jenkins_url, job_name, build_id)
        response = requests.get(url, verify='/etc/ssl/certs/Corvil-CA.pem')
        result = json.loads(response.text)

        # get job data
        job_url = "%s/job/%s/%s/api/json" %(jenkins_url, job_name, build_id)
        response = requests.get(job_url, verify='/etc/ssl/certs/Corvil-CA.pem')
        job = json.loads(response.text)
        timestamp = datetime.datetime.fromtimestamp(job['timestamp']/1000).strftime('%Y/%m/%d %H:%M:%S')

        # get console output ( revision )
        console_url = "%s/job/%s/%s/consoleText" %(jenkins_url, job_name, build_id)
        response = requests.get(console_url, verify='/etc/ssl/certs/Corvil-CA.pem')
        m = re.match('.*At revision (?P<revision>\d+)\n', response.text, re.DOTALL)
        if m:
            revision = m.groupdict().values()[0]
        else:
            raise "Revision not found for build %s" % build_id

    except Exception:
        print "No results for %s" % build_id
        return False

    json_file = open('data.json','w')
    if 'childReports' in result:
       result = result['childReports'][0]['result']

    for suite in result['suites']:
        for case in suite['cases']:
            line = '{'
            line += '"@timestamp": "%s", ' % timestamp
            line += '"tags": "cnn", '
            line += '"job_name": "%s", ' % job_name.split('/')[-1:]
            line += '"build_id": "%s", ' % build_id
            line += '"revision": "%s", ' % revision
            line += '"source": "%s", ' % source
            line += '"type": "%s", ' % the_type
            line += '"category": "%s", ' % category
            line += '"job_duration": "%f", ' % job['duration']
            line += '"namespace": "%s", ' % namespace
            line += '"brand": "%s", ' % brand
            line += '"file": "%s", ' % suite['name']
            line += '"suite_duration": "%f", ' % suite['duration']
            line += '"stdout": "%s", ' % ''
            line += '"stderr": "%s", ' % scape(case.get('stderr',''))
            line += '"class_name": "%s", ' % case['className']
            line += '"test_name": "%s", ' % case['name']
            line += '"test_duration": "%f", ' % case['duration']
            line += '"skipped": "%s", ' % str(case['skipped']).lower()
            line += '"failed_since": "%s", ' % case['failedSince']
            line += '"error_stack_trace": "%s", ' % scape(case.get('errorStackTrace', ''))

            if case['status'].upper() in ['PASSED', 'FIXED', 'SKIPPED']:
                line += '"status": "Pass"'
            else:
                line += '"status": "Fail"'

            line += "}\n"

            hash_object = hashlib.sha512(line)
            test_case_id = hash_object.hexdigest()

            json_file.write('{ "index" : {"_index": "test", "_type": "integration", "_id": "%s"}}\n' % test_case_id)
            json_file.write(line)

    json_file.close()
    return True


if __name__ == "__main__":
    for build in range(100):
        if process(build):
            send_to_elastic()
