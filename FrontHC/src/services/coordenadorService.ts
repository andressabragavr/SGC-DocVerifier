import axios from 'axios';

const API_URL = 'http://localhost:3000'; 

export default {
  async getAlunosComCertificados() {
    const res = await axios.get(`${API_URL}/certificados/validacao`);
    return res.data;
  },
  async aprovarCertificado(id: string) {
    return axios.put(`${API_URL}/certificados/${id}/aprovar`);
  },
  async rejeitarCertificado(id: string) {
    return axios.delete(`${API_URL}/certificados/${id}`);
  }
};
