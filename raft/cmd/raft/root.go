package raft

import (
	"os"

	"github.com/bamboovir/raft/lib/raft"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var (
	logger = log.WithField("cmd", "raft")
)

func ExitWrapper(err error) {
	if err != nil {
		logger.Errorf("command err: %v", err)
		os.Exit(1)
	}
}

type RootArgs struct {
	id      int
	port    int
	cluster string
}

func RootArgsCollector(cmd *cobra.Command) *RootArgs {
	args := &RootArgs{}
	cmd.Flags().IntVar(&args.id, "id", 1, "node ID")
	cmd.Flags().IntVar(&args.port, "port", 6666, "key-value server port")
	cmd.Flags().StringVar(&args.cluster, "cluster", "http://127.0.0.1:8000", "comma separated cluster peers")
	return args
}

func RootCMDMain(args *RootArgs) (err error) {
	logger.Infof("raft clusters [%s]", args.cluster)
	logger.Infof("kv server [http://127.0.0.1:%d]", args.port)
	raft.Start(args.cluster, args.id, args.port, false)
	return nil
}

func NewRootCMD() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "raft",
		Short: "raft",
		Long:  "raft",
	}

	args := RootArgsCollector(cmd)

	cmd.Run = func(cmd *cobra.Command, _ []string) {
		err := RootCMDMain(args)
		ExitWrapper(err)
	}

	return cmd
}
