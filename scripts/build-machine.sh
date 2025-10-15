docker build -t build-env .
docker run -v /home/jowens/.ssh:/root/.ssh -it build-env /root/Projects/build-publish-deb.sh