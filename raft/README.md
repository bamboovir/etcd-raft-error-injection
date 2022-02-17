# Raft

---

## Development Environment configuration

### Golang

[Install](https://golang.org/doc/install)

```bash
# go version >= 1.17
go version
go install golang.org/x/tools/cmd/goimports@latest
go get -u github.com/rakyll/gotest
```

### VSCode

```bash
# extension id golang.go
code --install-extension golang.go
```

### Etcd

We need to use some of etcd's private APIs to build our raft program. :)
You just need to clone etcd repo at the same level.
go.mod will automatically redirect these dependencies to your cloned repo.

```bash
git clone --depth=1 "https://github.com/etcd-io/etcd"
```

### Commonly used quick commands

Fmt Code

```bash
bash ./script/fmt.bash
```

Build raft static binary to ./bin

```bash
bash ./script/raft/build.bash
```

Build raft docker image

```bash
bash ./script/raft/build_docker_image.bash
```

Run raft docker image

```bash
docker run --rm -it --network="host" "docker.io/library/raft:dev"
```

Test Spec

```bash
gotest -mod vendor -v ./<>
```

Test All

```bash
gotest -mod vendor -v ./...
```

Trace log

```bash
LOG=trace
```

Json log

```bash
LOG=json
```

## Update deps

```bash
go mod vendor
```

## Usage

```bash
docker run --rm -it --network="host" "docker.io/library/raft:dev" --id 1 --cluster "http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002" --port "9000"
docker run --rm -it --network="host" "docker.io/library/raft:dev" --id 2 --cluster "http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002" --port "9001"
docker run --rm -it --network="host" "docker.io/library/raft:dev" --id 3 --cluster "http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002" --port "9002"
docker run --rm -it --network="host" "curlimages/curl:latest" -L http://127.0.0.1:9000/key -XPUT -d test
docker run --rm -it --network="host" "curlimages/curl:latest" -L http://127.0.0.1:9000/key
```

```bash
./bin/raft --id 1 --cluster http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002 --port 9000
./bin/raft --id 2 --cluster http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002 --port 9001
./bin/raft --id 3 --cluster http://127.0.0.1:8000,http://127.0.0.1:8001,http://127.0.0.1:8002 --port 9002
```

```bash
curl -L http://127.0.0.1:9000/key -XPUT -d test
curl -L http://127.0.0.1:9000/key
curl -L http://127.0.0.1:9001/key
curl -L http://127.0.0.1:9002/key
```

kill 3

```bash
curl -L http://127.0.0.1:9000/key
curl -L http://127.0.0.1:9001/key
curl -L http://127.0.0.1:9002/key
```

restart 3

```bash
curl -L http://127.0.0.1:9002/key
```

kill 2, 3

```bash
# no update until 2 or 3 start
curl -L http://127.0.0.1:9000/key -XPUT -d test1
curl -L http://127.0.0.1:9000/key
```

restart 2

```bash
curl -L http://127.0.0.1:9000/key
curl -L http://127.0.0.1:9001/key
```
