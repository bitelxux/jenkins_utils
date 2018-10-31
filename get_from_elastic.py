#connect to our cluster
from elasticsearch import Elasticsearch

es = Elasticsearch('https://elastic:changeme@elasticsearch.local.corvil.com:9200', ca_certs='/etc/ssl/certs/Corvil-CA.pem')
es.search(index="test", body={"query": {"match": {'tag':'cnn'}}})
