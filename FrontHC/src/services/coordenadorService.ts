import api from "./api";

interface AtividadePendente {
    id: number;
    nomeAluno: string; //alunoNome: string;
    ra: string; //alunoRA: string;
    tituloCertificado: string;
    dataEnvio: string;
    arquivoUrl: string; //
}

interface ResultadoValidacao {
    certificadoId: number;
    aprovado: boolean;
    horasValidadas?: number;
    observacao?: string;
}

interface DadosRelatorio {
    ra: string;
    nomeAluno: string;
    curso: string;
    certificados: {
        id: number;
        titulo: string;
        horas: number;
        arquivoUrl: string; //
    }[];
}

const coordenadorService = {
    getAtividadesPendentes: async (): Promise<AtividadePendente[]> => {
        const response = await api.get('/coodenador/atividades-pendentes');
        return response.data;
    },

    validarAtividade: async (dados: ResultadoValidacao) => {
        return await api.post('/coordenador/validar-atividade', dados);
    },

    buscarAlunoPorRA: async (ra: string) => {
        const response = await api.get(`/coordenador/alunos/${ra}`); //
        return response.data;
    },

    gerarRelatorio: async (ra: string): Promise<DadosRelatorio> => {
        const response = await api.get(`/coordenador/relatorio/${ra}`);
        return response.data;
    }
};

export default coordenadorService;