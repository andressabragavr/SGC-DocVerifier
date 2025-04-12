import api from './api';

interface LoginResponse {
    token: string;
    user: {
        id: number;
        name: string;
        email: string;
    }
}

interface RegisterData {
    name: string;
    email: string;
    ra: string;
    password: string;
}

// interface LoginResponse {
//     token: string;
//     usuario: {
//         id: number;
//         nome: string;
//         tipo: 'aluno' | 'coordenador';
//     };
// }

const authService = {
    login: async (email: string, password: string): Promise<LoginResponse> => {
        const response = await api.post('/auth/login', { email, password });

        //Store the toke in local storage
        localStorage.setItem('token', response.data.token);

        return response.data;
    },

    // cadastrarAluno: async(dados: CadastroData) => {
    //     return await api.post('/alunos/cadastro', dados);
    // },

    // verificarAuth: () => {
    //     return localStorage.getItem('token') !== null;
    // },

    register: async (data: RegisterData): Promise<void> => {
        await api.post('/auth/register', data);
    },

    logout: () => {
        localStorage.removeItem('token');
    }
};

export default authService;