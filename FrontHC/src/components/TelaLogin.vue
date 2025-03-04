<script lang="ts">
  import { defineComponent, reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import authService from '@/services/authService';
  
  export default defineComponent({
    name: 'LoginForm',
    setup() {
      const router = useRouter();
      const login = ref<string>('');
      const password = ref<string>('');
      const errorMessage = ref('');
  
      const handleLogin = () => {
        console.log('Login:', login.value);
        console.log('Senha:', password.value);
        router.push('/TelaInicialAluno');
      };
  
      const redirectToRegister = () => {
        router.push('/TelaCadastro'); 
      };
  
      return {
        login,
        password,
        handleLogin,
        redirectToRegister,
      };
    },
  });
</script>

<template>
     <img src="../assets/Logo-Branco.png" alt="Logo" class="logo">
     <main>
        <h1 class="title">Horas Complementares</h1>
        <div class="login-form">
            <input type="text" placeholder="Login" v-model="login" class="input-field"/>
            <input type="password" placeholder="Senha" v-model="password" class="input-field"/>
            <button @click="handleLogin" class="login-button">Entrar</button>
            <button @click="redirectToRegister" class="register-button">Cadastrar</button>
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
    padding-bottom: 30px;
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
  
.register-button {
    width: 100%;
    max-width: 300px;
    padding: 10px;
    margin: 5px 0;
    background-color: transparent;
    color: #FF8C00;
    border: 2px solid #FF8C00;
    border-radius: 10px;
    font-size: 15px;
    font-weight: bold;
    font-family: 'League Spartan', sans-serif;
    cursor: pointer;
}

.register-button:hover {
    background-color: #FF4500;
    color: #fff;
}
</style>  