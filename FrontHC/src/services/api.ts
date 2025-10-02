// services/api.ts
import axios from 'axios';

const api = axios.create({
  //baseURL: 'http://backend:3000', // nome do serviço do backend no docker-compose
  baseURL: process.env.VUE_APP_API_URL || "http://localhost:3000",
});

export default api;
