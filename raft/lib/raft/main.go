// Copyright 2015 The etcd Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package raft

import (
	"io"
	"os"
	"strings"

	"github.com/bamboovir/raft/lib/metrics"
	"go.etcd.io/etcd/raft/v3/raftpb"
)

func Start(cluster string, id int, kvport int, monitorAddr string, metricsLogPath string, join bool) (err error) {
	var logF io.WriteCloser
	if metricsLogPath == "-" {
		logF = os.Stdout
	} else {
		logF, err = os.OpenFile(metricsLogPath, os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return err
		}
	}
	defer logF.Close()

	metricsLogger := metrics.NewLogger(logF)

	proposeC := make(chan string)
	defer close(proposeC)
	confChangeC := make(chan raftpb.ConfChange)
	defer close(confChangeC)

	// raft provides a commit stream for the proposals from the http api
	var kvs *kvstore
	getSnapshot := func() ([]byte, error) { return kvs.getSnapshot() }
	rc, commitC, errorC, snapshotterReady := newRaftNode(id, strings.Split(cluster, ","), join, getSnapshot, proposeC, confChangeC, metricsLogger)

	raftStateService := newHttpRaftStateAPI(rc)
	raftStateService.serve(monitorAddr, errorC)

	kvs = newKVStore(<-snapshotterReady, proposeC, commitC, errorC)
	// the key-value http handler will propose updates to raft
	serveHttpKVAPI(kvs, kvport, confChangeC, errorC)
	return nil
}
