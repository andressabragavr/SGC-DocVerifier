import axios from 'axios';

const apiIA = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export const getIAResponse = async (input: string) => {
  const response = await apiIA.post('/ia', { input });
  return response.data;
};