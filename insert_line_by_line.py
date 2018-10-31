import os
cmd = 'curl -i -XPOST --user cnovo:eliquela -H "Content-Type: application/json"  "http://elasticsearch.local.corvil.com:9200/test/doc" --data-binary @"insert.json"'

for line in open('data.json').readlines():
    with open("insert.json","w") as f:
        f.write(line)
    result = os.system(cmd)
    
