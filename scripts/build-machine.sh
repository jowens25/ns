docker build -t build-env .
docker run -v /home/jowens/.ssh:/root/.ssh -it build-env /root/Projects/ns/scripts/build-publish-deb.sh
