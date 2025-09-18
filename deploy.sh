git pull --recurse-submodules

./scripts/build-deb.sh

scp ns_1.0.2_arm64.deb root@10.1.10.220:~/