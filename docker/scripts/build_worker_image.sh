cp -r worker/. docker/.build
cd docker
docker build -t golem-fleet-battle .
gvmkit-build golem-fleet-battle:latest