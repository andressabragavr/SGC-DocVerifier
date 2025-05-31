<script lang="ts">
// TelaCadastro.vue
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';

export default defineComponent({
  name: 'RegisterForm',
  setup() {
    const router = useRouter();
    const name = ref('');
    const email = ref('');
    const password = ref('');
    const ra = ref('');
    const tipo = ref('aluno'); // Novo campo com valor padrão
    const errorMessage = ref('');
    const isLoading = ref(false);

    const handleRegister = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';

        await authService.register({
          name: name.value,
          email: email.value,
          password: password.value,
          ra: ra.value,
          tipo: tipo.value 
        });

        router.push('/');
      } catch (error) {
        errorMessage.value = 'Erro ao realizar cadastro. Tente novamente.';
        console.error('Register error:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const redirectToLogin = () => {
      router.push('/');
    };

    return {
      name,
      email,
      password,
      ra,
      tipo,
      errorMessage,
      isLoading,
      handleRegister,
      redirectToLogin,
    };
  },
});
</script>

<template>
  <img src="../assets/Logo-Branco.png" alt="Logo" class="logo" />
  <main>
    <h1 class="title">Cadastro de Usuário</h1>
    <div class="register-form">
      <input type="text" v-model="name" placeholder="Nome completo" class="input-field" :disabled="isLoading" />
      <input type="text" v-model="email" placeholder="E-mail" class="input-field" :disabled="isLoading" />
      <input type="password" v-model="password" placeholder="Senha" class="input-field" :disabled="isLoading" />
      <input type="text" v-model="ra" placeholder="RA" class="input-field" :disabled="isLoading" />

      <!-- Campo tipo -->
      <select v-model="tipo" class="input-field" :disabled="isLoading">
        <option value="aluno">Aluno</option>
        <option value="coordenador">Coordenador</option>
      </select>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <button @click="handleRegister" class="register-button" :disabled="isLoading">
        {{ isLoading ? 'Cadastrando...' : 'Cadastrar' }}
      </button>
      <button @click="redirectToLogin" class="login-button" :disabled="isLoading">Voltar para página de Login</button>
    </div>
  </main>
</template>

<style scoped>
.logo {
  height: 7rem;
  margin-left: 30px;
  margin-top: 20px;
}

.title {
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin-top: 4rem;
  padding-bottom: 30px;
}

.register-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.input-field {
  width: 100%;
  max-width: 300px;
  padding: 10px;
  margin: 5px 0;
  border: 2px solid #ccc;
  border-radius: 10px;
  font-size: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.register-button {
  width: 100%;
  max-width: 300px;
  padding: 10px;
  margin: 5px 0;
  background-color: #FF8C00;
  color: #fff;
  border: 2px solid #FF8C00;
  border-radius: 10px;
  font-size: 15px;
  font-weight: bold;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  cursor: pointer;
}

.register-button:hover {
  background-color: #FF4500;
  color: #fff;
}

.error-message {
  color: #ff0000;
  font-size: 14px;
  margin-top: 10px;
  text-align: center;
}

.login-button {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 15px;
  text-decoration: underline;
  margin-top: -3px;
}
</style>
