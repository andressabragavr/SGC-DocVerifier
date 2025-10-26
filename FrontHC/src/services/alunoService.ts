import api from './api';

const getCertificados = async () => {
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
  return api.get(`/usuarios/${usuario.ra}/certificados`); 
};

const getCertificadosPorRa = async (ra: string) => {
  return api.get(`/usuarios/${ra}/certificados`); 
};

export default {
  getCertificados,
  getCertificadosPorRa
};
