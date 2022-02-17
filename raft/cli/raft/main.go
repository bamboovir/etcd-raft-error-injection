package main

import (
	"os"

	"github.com/bamboovir/raft/cmd/raft"
	"github.com/bamboovir/raft/lib/logger"
	log "github.com/sirupsen/logrus"
)

func main() {
	logger.SetupLogger(log.StandardLogger())
	rootCMD := raft.NewRootCMD()
	if err := rootCMD.Execute(); err != nil {
		log.Errorf("%v\n", err)
		os.Exit(1)
	}
}
