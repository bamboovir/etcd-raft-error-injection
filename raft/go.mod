module github.com/bamboovir/raft

go 1.17

replace (
	go.etcd.io/etcd/api/v3 => ./etcd/api
	go.etcd.io/etcd/client/pkg/v3 => ./etcd/client/pkg
	go.etcd.io/etcd/client/v2 => ./etcd/client/v2
	go.etcd.io/etcd/client/v3 => ./etcd/client/v3
	go.etcd.io/etcd/etcdctl/v3 => ./etcd/etcdctl
	go.etcd.io/etcd/etcdutl/v3 => ./etcd/etcdutl
	go.etcd.io/etcd/pkg/v3 => ./etcd/pkg
	go.etcd.io/etcd/raft/v3 => ./etcd/raft
	go.etcd.io/etcd/server/v3 => ./etcd/server
	go.etcd.io/etcd/tests/v3 => ./etcd/tests
)

require (
	github.com/sirupsen/logrus v1.8.1
	github.com/spf13/cobra v1.3.0
	go.etcd.io/etcd/client/pkg/v3 v3.5.1
	go.etcd.io/etcd/raft/v3 v3.5.0
	go.etcd.io/etcd/server/v3 v3.0.0-00010101000000-000000000000
	go.uber.org/zap v1.21.0
)

require (
	github.com/beorn7/perks v1.0.1 // indirect
	github.com/cespare/xxhash/v2 v2.1.2 // indirect
	github.com/coreos/go-semver v0.3.0 // indirect
	github.com/dustin/go-humanize v1.0.0 // indirect
	github.com/gogo/protobuf v1.3.2 // indirect
	github.com/golang/protobuf v1.5.2 // indirect
	github.com/inconshreveable/mousetrap v1.0.0 // indirect
	github.com/matttproud/golang_protobuf_extensions v1.0.1 // indirect
	github.com/prometheus/client_golang v1.11.0 // indirect
	github.com/prometheus/client_model v0.2.0 // indirect
	github.com/prometheus/common v0.26.0 // indirect
	github.com/prometheus/procfs v0.6.0 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	github.com/xiang90/probing v0.0.0-20190116061207-43a291ad63a2 // indirect
	go.etcd.io/etcd/api/v3 v3.5.1 // indirect
	go.etcd.io/etcd/pkg/v3 v3.5.0 // indirect
	go.uber.org/atomic v1.7.0 // indirect
	go.uber.org/multierr v1.7.0 // indirect
	golang.org/x/net v0.0.0-20220105145211-5b0dc2dfae98 // indirect
	golang.org/x/sys v0.0.0-20211205182925-97ca703d548d // indirect
	golang.org/x/text v0.3.7 // indirect
	golang.org/x/time v0.0.0-20210220033141-f8bda1e9f3ba // indirect
	google.golang.org/genproto v0.0.0-20211208223120-3a66f561d7aa // indirect
	google.golang.org/grpc v1.42.0 // indirect
	google.golang.org/protobuf v1.27.1 // indirect
)
