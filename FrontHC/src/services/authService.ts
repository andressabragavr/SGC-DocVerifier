import api from './api';

interface LoginData {
    login: string;
    senha: string;
}

interface CadastroData {
    nomeAluno: string;
    curso: string;
    ra: string;
    senha: string;
}

interface LoginResponse {
    token: string;
    usuario: {
        id: number;
        nome: string;
        tipo: 'aluno' | 'coordenador';
    };
}

const authService = {
    login: async (dados: LoginData): Promise<LoginResponse> => {
        const response = await api.post('/auth/login', dados);

        if (response.data && response.data.token) {
            localStorage.setItem('token', response.data.token);
        }

        return response.data;
    },

    cadastrarAluno: async(dados: CadastroData) => {
        return await api.post('/alunos/cadastro', dados);
    },

    verificarAuth: () => {
        return localStorage.getItem('token') !== null;
    },

    logout: () => {
        localStorage.removeItem('token');
    }
};

export default authService;