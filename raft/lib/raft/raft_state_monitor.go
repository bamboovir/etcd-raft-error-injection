package raft

import (
	"net/http"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
	"go.etcd.io/etcd/raft/v3"
)

var (
	logger = log.WithField("src", "/lib/raft/raft_state_monitor")
)

type httpRaftStateAPI struct {
	node *raftNode
}

func newHttpRaftStateAPI(node *raftNode) *httpRaftStateAPI {
	return &httpRaftStateAPI{
		node: node,
	}
}

func (h *httpRaftStateAPI) RaftNode() raft.Node {
	return h.node.node
}

func (h *httpRaftStateAPI) raftState(c *gin.Context) {
	msg, err := h.RaftNode().Status().MarshalJSON()
	if err != nil {
		logger.WithError(err).Error("fetch raft state failed")
		c.JSON(http.StatusNotFound, gin.H{})
		return
	}
	c.Data(http.StatusOK, gin.MIMEJSON, msg)
}

func (h *httpRaftStateAPI) serve(addr string, errorC <-chan error) {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.GET("/raft/state", h.raftState)

	go func() {
		if err := router.Run(addr); err != nil {
			logger.Fatal(err)
		}
	}()

	go func() {
		// exit when raft goes down
		if err, ok := <-errorC; ok {
			logger.Fatal(err)
		}
	}()
}
