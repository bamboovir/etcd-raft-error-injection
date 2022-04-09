import http from 'k6/http';
import { check } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    ramping_arrival_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 360,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 250,
      stages: [
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
      ],
    },
  },
};

export default function () {
  const raftClusterAddrs = `${__ENV.RAFT_CLUSTER_ADDRS}`
  const raftClusters = raftClusterAddrs.split(",")
  const sendRequestToNode = (addr) => {
    const url = addr + "/key"
    const payloadSize = randomIntBetween(5, 20)
    const value = randomString(payloadSize)
    const res = http.put(url, value)
    return res.status === 200
  }
  const sendRequestToCluster = (cluster) => {
    for (let addr of cluster) {
      let rst = sendRequestToNode(addr)
      if (rst) {
        return true
      }
    }
    return false
  }

  const rst = sendRequestToCluster(raftClusters)
  check(rst, {
    'ok': (r) => r,
  });
}
