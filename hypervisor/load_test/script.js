import http from 'k6/http';
import { sleep } from 'k6';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  stages: [
    { duration: '5s', target: 20 },
    { duration: '5s', target: 10 },
    { duration: '5s', target: 20 },
  ],
};

export default function () {
  const url = "http://127.0.0.1:6666/key"
  const value = randomString(5)
  http.put(url, value)
}
