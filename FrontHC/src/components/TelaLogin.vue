<script lang="ts">
//TelaLogin.vue
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import authService from '@/services/authService';

export default defineComponent({
  name: 'LoginForm',
  setup() {
    const router = useRouter();
    const login = ref<string>('');
    const password = ref<string>('');
    const errorMessage = ref('');
    const isLoading = ref(false);

    const handleLogin = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        const response = await authService.login(login.value, password.value);
        localStorage.setItem('usuario', JSON.stringify(response.data));
        router.push('/TelaInicialAluno');
      } catch (error) {
        errorMessage.value = 'Credenciais inválidas. Tente novamente.';
        console.error('Login error:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const redirectToRegister = () => {
      router.push('/TelaCadastro');
    };

    return {
      login,
      password,
      errorMessage,
      isLoading,
      handleLogin,
      redirectToRegister,
    };
  },
});
</script>

<template>
     <img src="../assets/Logo-Branco.png" alt="Logo" class="logo">
     <main>
        <h1 class="title">Login</h1>
        <div class="login-form">
            <input type="text" placeholder="Login" v-model="login" class="input-field" :disabled="isLoading"/>
            <input type="password" placeholder="Senha" v-model="password" class="input-field" :disabled="isLoading"/>
            <P v-if="errorMessage" class="error-message">{{ errorMessage }}</P>
            <button @click="handleLogin" class="login-button" :disabled="isLoading">{{ isLoading? 'Carregando...' : 'Entrar' }}</button>
            <p class="no-account">Não tem uma conta?<button @click="redirectToRegister" class="register-button" :disabled="isLoading">Cadastre-se</button></p>
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
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    padding-bottom: 70px;
}

.login-form {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px
}
  
.input-field {
    width: 100%;
    max-width: 300px;
    padding: 10px;
    margin: 5px 0;
    border: 2px solid #ccc;
    border-radius: 10px;
    font-size: 16px;
    font-family: 'League Spartan', sans-serif;
}
  
.login-button {
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
    font-family: 'League Spartan', sans-serif;
    cursor: pointer;
}

.login-button:hover {
    background-color: #FF4500;
}

.no-account {
    font-family: 'League Spartan', sans-serif;
    font-size: 15px;
    color: #000;
    margin-top: 15px;
}
  
.register-button {
    /* width: 100%;
    max-width: 300px;
    padding: 10px; */
    margin-left: 10px;
    /* background-color: transparent; */
    color: #FF8C00;
    /* border: 2px solid #FF8C00;
    border-radius: 10px; */
    font-size: 15px;
    font-weight: bold;
    font-family: 'League Spartan', sans-serif;
    cursor: pointer;
}

.register-button:hover {
    color: #FF4500;
}

.error-message {
  color: #ff0000;
  font-size: 14px;
  margin-top: 10px;
  text-align: center;
}
</style>  