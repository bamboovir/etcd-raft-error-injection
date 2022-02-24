import http from 'k6/http';
import { sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    ramping_arrival_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 100,
      stages: [
        { target: 200, duration: '10s' },
        { target: 0, duration: '10s' },
      ],
    },
  },
};

export default function () {
  // const url = "http://127.0.0.1:6666/key"
  // const value = randomString(5)
  // http.put(url, value)
  http.get('http://127.0.0.1:5000/raft/state');
}
