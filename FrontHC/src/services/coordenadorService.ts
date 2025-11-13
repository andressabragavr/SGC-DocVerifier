import axios from 'axios';

const API_URL = 'http://localhost:3000';

export default {
  async getIndicadoresPorTipo() {
    const res = await axios.get(`${API_URL}/indicadores/tipos`);
    return res.data; // { data: [{ tipoAtividade, count }] }
  },

  async getGraficoTipos() {
    const res = await axios.get(`${API_URL}/indicadores/grafico-tipos`);
    return res.data; // { imageUrl }
  },
  
  async buscarAlunoPorRA(ra: string) {
    const res = await axios.get(`${API_URL}/certificados/busca`, {
      params: { filtro: 'ra', valor: ra }
    });
    return res.data;
  }
};
