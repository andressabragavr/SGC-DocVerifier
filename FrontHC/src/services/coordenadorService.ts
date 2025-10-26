import axios from 'axios';

const API_URL = 'http://localhost:3000';

export default {
  async buscarAlunoPorRA(ra: string) {
    const res = await axios.get(`${API_URL}/certificados/busca`, {
      params: { filtro: 'ra', valor: ra }
    });
    return res.data;
  }
};
