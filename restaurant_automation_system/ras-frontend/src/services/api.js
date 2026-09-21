import axios from 'axios';

const BASE_URL =
  process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});
