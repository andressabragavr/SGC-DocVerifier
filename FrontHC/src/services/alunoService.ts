// interface DadosAluno {
//     nomeAluno: string;
//     numCertificados: number; 
//     horasLancadas: number;
//     horasFaltantes: number;
//     horasExigidas: number;
// }

// interface Certificado {
//     id: number;
//     titulo: string;
//     categoria: string;
//     tipoAtividade: string;
//     dataEnvio: string;
//     horas: number;
//     arquivoUrl: string; //
// }

// // interface HistoricoCertificado {
// //     id: number;
// //     titulo: string;
// //     categoria: string;
// //     tipoAtividade: string;
// //     dataEnvio: string;
// //     horas: number;
// //     arquivoUrl: string; //
// // }

// const alunoService = {
//     getDadosAluno: async (): Promise<DadosAluno> => {
//         const response = await api.get('/aluno/dashboard');
//         return response.data;
//     },

//     enviarCertificado: async (formData: FormData) => {
//         return await api.post('/certificados', formData, {
//             headers: {
//                 'Content-Type': 'multipart/form-data',
//             }
//         });
//     },

//     getHistoricoCertificados: async (): Promise<Certificado[]> => {
//         const response = await api.get('/certificados/historico');
//         return response.data;
//     },

//     getCertificadoPdf: async (certificadoId: number): Promise<Blob> => {
//         const response = await api.get(`/certificados/${certificadoId}/pdf`, {
//             responseType: 'blob',
//         });
//         return response.data;
//     }
// };

// export default alunoService;

import api from './api';

const getCertificados = async () => {
  const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');
  return api.get(`/usuarios/${usuario.ra}/certificados`);
};

export default {
  getCertificados
};
