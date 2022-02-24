package metrics

import (
	"io"
	"time"

	log "github.com/sirupsen/logrus"
)

type ThroughputEntry struct {
	NodeID    string `json:"node_id"`
	Timestamp int64  `json:"timestamp"`
	BytesSize int    `json:"bytes_size"`
}

type LatencyEntry struct {
	Timestamp int64 `json:"timestamp"`
	Latency   int64 `json:"latency"`
}

func NewLatencyEntry(timestamp time.Time, latency time.Duration) *LatencyEntry {
	return &LatencyEntry{
		Timestamp: timestamp.UnixNano(),
		Latency:   latency.Nanoseconds(),
	}
}

func NewThroughputEntry(nodeID string, timestamp time.Time, bytesSize int) *ThroughputEntry {
	return &ThroughputEntry{
		NodeID:    nodeID,
		Timestamp: timestamp.UnixNano(),
		BytesSize: bytesSize,
	}
}

func NewLogger(w io.Writer) *log.Logger {
	logger := log.New()
	logger.SetFormatter(&log.JSONFormatter{
		DisableTimestamp: true,
		PrettyPrint:      false,
	})
	logger.SetReportCaller(false)
	logger.SetLevel(log.TraceLevel)
	logger.SetOutput(w)
	return logger
}
