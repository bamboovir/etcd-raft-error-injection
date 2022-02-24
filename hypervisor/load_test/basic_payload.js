import http from 'k6/http';
import { check } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    ramping_arrival_rate: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '1s',
      preAllocatedVUs: 10,
      maxVUs: 100,
      stages: [
        { target: 10, duration: '50s' },
        { target: 0, duration: '50s' },
      ],
    },
  },
};

export default function () {
  const baseURL = `${__ENV.BASEURL}`
  const url = baseURL + "/key"
  const value = randomString(5)
  const res = http.put(url, value)
  check(res, {
    'is status 200': (r) => r.status === 200,
  });
}
