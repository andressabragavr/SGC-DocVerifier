import axios from 'axios';

const API_URL = 'https://tccbackend2-hccfh0gyeperdjbx.brazilsouth-01.azurewebsites.net';

export default {
  async buscarAlunoPorRA(ra: string) {
    const res = await axios.get(`${API_URL}/certificados/busca`, {
      params: { filtro: 'ra', valor: ra }
    });
    return res.data;
  }
};
