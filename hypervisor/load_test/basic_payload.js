import http from 'k6/http';
import { check } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    ramping_arrival_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 0,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 250,
      stages: [
        { target: 0, duration: '1s' },
        { target: 0, duration: '19s' },
        { target: 10, duration: '1s' },
        { target: 10, duration: '19s' },
        { target: 20, duration: '1s' },
        { target: 20, duration: '19s' },
        { target: 30, duration: '1s' },
        { target: 30, duration: '19s' },
        { target: 40, duration: '1s' },
        { target: 40, duration: '19s' },
        { target: 50, duration: '1s' },
        { target: 50, duration: '19s' },
        { target: 60, duration: '1s' },
        { target: 60, duration: '19s' },
        { target: 70, duration: '1s' },
        { target: 70, duration: '19s' },
        { target: 80, duration: '1s' },
        { target: 80, duration: '19s' },
        { target: 90, duration: '1s' },
        { target: 90, duration: '19s' },
        { target: 100, duration: '1s' },
        { target: 100, duration: '19s' },
        { target: 110, duration: '1s' },
        { target: 110, duration: '19s' },
        { target: 120, duration: '1s' },
        { target: 120, duration: '19s' },
        { target: 130, duration: '1s' },
        { target: 130, duration: '19s' },
        { target: 140, duration: '1s' },
        { target: 140, duration: '19s' },
        { target: 150, duration: '1s' },
        { target: 150, duration: '19s' },
        { target: 160, duration: '1s' },
        { target: 160, duration: '19s' },
        { target: 170, duration: '1s' },
        { target: 170, duration: '19s' },
        { target: 180, duration: '1s' },
        { target: 180, duration: '19s' },
        { target: 190, duration: '1s' },
        { target: 190, duration: '19s' },
        { target: 200, duration: '1s' },
        { target: 200, duration: '19s' },
        { target: 210, duration: '1s' },
        { target: 210, duration: '19s' },
        { target: 220, duration: '1s' },
        { target: 220, duration: '19s' },
        { target: 230, duration: '1s' },
        { target: 230, duration: '19s' },
        { target: 240, duration: '1s' },
        { target: 240, duration: '19s' },
        { target: 250, duration: '1s' },
        { target: 250, duration: '19s' },
        { target: 260, duration: '1s' },
        { target: 260, duration: '19s' },
        { target: 270, duration: '1s' },
        { target: 270, duration: '19s' },
        { target: 280, duration: '1s' },
        { target: 280, duration: '19s' },
        { target: 290, duration: '1s' },
        { target: 290, duration: '19s' },
        { target: 300, duration: '1s' },
        { target: 300, duration: '19s' },
        { target: 310, duration: '1s' },
        { target: 310, duration: '19s' },
        { target: 320, duration: '1s' },
        { target: 320, duration: '19s' },
        { target: 330, duration: '1s' },
        { target: 330, duration: '19s' },
        { target: 340, duration: '1s' },
        { target: 340, duration: '19s' },
        { target: 350, duration: '1s' },
        { target: 350, duration: '19s' },
        { target: 360, duration: '1s' },
        { target: 360, duration: '19s' },
        { target: 370, duration: '1s' },
        { target: 370, duration: '19s' },
        { target: 380, duration: '1s' },
        { target: 380, duration: '19s' },
        { target: 390, duration: '1s' },
        { target: 390, duration: '19s' },
        { target: 400, duration: '1s' },
        { target: 400, duration: '19s' },
        { target: 410, duration: '1s' },
        { target: 410, duration: '19s' },
        { target: 420, duration: '1s' },
        { target: 420, duration: '19s' },
        { target: 430, duration: '1s' },
        { target: 430, duration: '19s' },
        { target: 440, duration: '1s' },
        { target: 440, duration: '19s' },
        { target: 450, duration: '1s' },
        { target: 450, duration: '19s' },
        { target: 460, duration: '1s' },
        { target: 460, duration: '19s' },
        { target: 470, duration: '1s' },
        { target: 470, duration: '19s' },
        { target: 480, duration: '1s' },
        { target: 480, duration: '19s' },
        { target: 490, duration: '1s' },
        { target: 490, duration: '19s' },
        { target: 500, duration: '1s' },
        { target: 500, duration: '19s' },
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
