
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import os
from pprint import pprint as pp
import requests
import re
import subprocess
import sys
import time

jenkins_url = "https://jenkins.ci.local.corvil.com/"
elastic_url = "http://elasticsearch.local.corvil.com:9200/_bulk"
job_name, build_id, namespace, source, the_type, category, brand, revision = sys.argv[1:]

# TODO get the timestamp from job_url REST
# TODO get the revision from job_url REST

#job_url = 'https://jenkins.ci.local.corvil.com/job/Frontend/job/frontend-actions/31/api/json'
#test_results_url = "https://jenkins.ci.local.corvil.com/job/Frontend/job/frontend-dashboards/31"

#elasticsearch_bulk_cmd = 'curl -XPOST -H "Content-Type: application/json, "
#    "%s" --data-binary @data.json' % elastic_url

def scape(text):
    text = text and text.replace('"', r'\"').replace('\n', r'\n').replace('\t', r'  ').replace('|', r' ') or ''
    return text

def send_to_elastic(data_file):
    req = requests.post(elastic_url,
        Authentication = '72a99479-d6d9-4c89-807c-481f4fc0ecdf',
        data = file(data_file,'rb').read())

# Get tests results
url = '%s/job/%s/%s/testReport/api/json' % (jenkins_url, job_name, build_id)
response = requests.get(url, verify='/etc/ssl/certs/Corvil-CA.pem')
result = json.loads(response.text)

# get job data
job_url = "%s/job/%s/%s/api/json" %(jenkins_url, job_name, build_id)
response = requests.get(job_url, verify='/etc/ssl/certs/Corvil-CA.pem')
job = json.loads(response.text)
timestamp = datetime.datetime.fromtimestamp(job['timestamp']/1000).strftime('%Y/%m/%d %H:%M:%S')

json_file = open('data.json','w')

for suite in result['suites']:
    for case in suite['cases']:
        line = '{'
        line += '"@timestamp": "%s", ' % timestamp
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
        line += '"stderr": "%s", ' % scape(case['stderr'])
        line += '"class_name": "%s", ' % case['className']
        line += '"test_name": "%s", ' % case['name']
        line += '"test_duration": "%f", ' % case['duration']
        line += '"skipped": "%s", ' % case['skipped']
        line += '"failed_since": "%s", ' % case['failedSince']
        line += '"error_stack_trace": "%s", ' % scape(case['errorStackTrace'])

        if case['status'].upper() in ['PASSED', 'FIXED', 'SKIPPED']:
            line += '"status": "Pass"'
        else:
            line += '"status": "Fail"'

        line += "}\n"

        # for bulk ... json_file.write('{ "index" : {"_index": "test", "_type": "integration"}}\n')
        json_file.write(line)

json_file.close()


send_to_elastic("data.json")
