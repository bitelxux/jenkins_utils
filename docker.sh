#docker run --add-host=host:172.17.0.1 -u 0 -d --name jenkins -p 8080:8080 -p 50000:50000 -v /tmp/jenkins:/var/jenkins_home jenkins
docker run --add-host=host:172.17.0.1 -u 0 -d --name jenkins -p 8080:8080 -p 50000:50000 jenkins
docker run  --add-host=host:172.17.0.1 -d -p 9200:9200 -p9300:9300 --name elastic docker.elastic.co/elasticsearch/elasticsearch:6.1.2
docker run --name kibana --add-host=host:172.17.0.1 -u 0 -e ELASTICSEARCH_URL=http://172.17.0.1:9200 -p 5601:5601 -d docker.elastic.co/kibana/kibana-oss:6.1.2
#docker run -u 0 -d --add-host=host:172.17.0.1 --name grafana -p 3000:3000 grafana/grafana
