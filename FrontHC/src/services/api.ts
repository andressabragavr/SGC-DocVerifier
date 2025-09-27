// services/api.ts
import axios = require('axios');

const api = axios.create({
  baseURL: 'http://backend:3000', // nome do serviço do backend no docker-compose
});

export default api;

