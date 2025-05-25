import api from './api';

interface RegisterData {
  name: string;
  email: string;
  password: string;
  ra: string;
}

const register = async (data: RegisterData) => {
  return api.post('/usuarios', data);
};

const login = async (ra: string, password: string) => {
  return api.post('/login', { ra, password });
};

export default {
  register,
  login,
};