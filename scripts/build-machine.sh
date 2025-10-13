docker build -t build-machine .
docker run -v /home/jowens/.ssh:/root/.ssh -it build-machine
