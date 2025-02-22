<script lang="ts">
  import { defineComponent, ref } from 'vue';
  import { useRouter } from 'vue-router';
  
  export default defineComponent({
    name: 'RegisterForm',
    setup() {
      const fullName = ref<string>('');
      const curso = ref<string>('');
      const ra = ref<string>('');
      const password = ref<string>('');
      const router = useRouter();
  
      const handleRegister = () => {
        console.log('Nome Completo:', fullName.value);
        console.log('Curso:', curso.value);
        console.log('RA:', ra.value);
        console.log('Senha:', password.value);
        router.push('/');
      };
  
      return {
        fullName,
        curso,
        ra,
        password,
        handleRegister,
      };
    },
  });
</script>

<template>
     <!-- <img src="../assets/LogoFacens.png" alt="Logo" class="logo"> -->
     <main>
        <h1 class="title">Horas Complementares</h1>
        <div class="register-form">
            <input type="text" placeholder="Nome Completo" v-model="fullName" class="input-field"/>
            <input type="text" placeholder="Curso" v-model="curso" class="input-field"/>
            <input type="text" placeholder="RA" v-model="ra" class="input-field"/>
            <input type="password" placeholder="Senha" v-model="password" class="input-field"/>
            <button @click="handleRegister" class="register-button">Cadastrar</button>
        </div>
     </main>
</template>
  
<style scoped>
.logo {
    height: 4.5rem;
    margin-bottom: 2rem;
    margin-top: 0.6rem;
    margin-left: 0.3rem;
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
</style>  