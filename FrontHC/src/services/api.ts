// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://tccbackend2-hccfh0gyeperdjbx.brazilsouth-01.azurewebsites.net',
});

export default api;
