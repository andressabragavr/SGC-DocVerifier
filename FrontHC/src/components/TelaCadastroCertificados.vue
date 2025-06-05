<script lang="ts">
import Banner from './Banner.vue';
import { defineComponent, ref, computed } from 'vue';
import Tooltip from './Tooltip.vue';
  
export default defineComponent({
    name: 'TelaCadastroCertificados',
    components: {Banner, Tooltip},

    data() {
      return {
        file: null as File | null,
        fileName: '',
      };
    },
    methods: {
      handleFileUpload(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
          this.file = target.files[0];
          this.fileName = this.file.name;
        }
      },
      triggerFileUpload() {
        (this.$refs.fileInput as HTMLInputElement).click();
      },
      submitForm() {
        if (this.file) {
          const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');

          const formData = new FormData();
          formData.append('arquivo', this.file);
          formData.append('ra', usuario.ra); // pega do localStorage
          formData.append('titulo', 'Curso de HTML, CSS e Bootstrap5');
          formData.append('categoria', 'Livre');
          formData.append('tipoAtividade', 'Curso de Formação Complementar');
          formData.append('dataEnvio', new Date().toISOString());
          formData.append('horasAtribuidas', '17');
          formData.append('status', 'Pendente');

          fetch('http://localhost:3000/certificados/upload', {
            method: 'POST',
            body: formData
          })
          .then(res => res.json())
          .then(data => {
            alert('Certificado enviado com sucesso!');
            console.log(data);
          })
          .catch(err => {
            console.error('Erro ao enviar certificado:', err);
            alert('Erro ao enviar certificado');
          });
        } else {
          alert('Por favor, selecione um arquivo antes de enviar.');
        }
      },
    },
});
</script>

<template>
    <Banner />
    <h1 class="title">Cadastro de Certificados</h1>
    <div class="upload-container">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="certificate">
            <button type="button" class="upload-button" @click="triggerFileUpload">Selecionar arquivo PDF</button>
          </label>
          <input type="file" id="certificate" @change="handleFileUpload" accept=".pdf" required ref="fileInput" />
        </div>
        <div v-if="fileName" class="file-info">
          <p class="file-name">Arquivo selecionado: {{ fileName }}</p>
        </div>
        <button type="submit" class="submit-button">Upload</button>
      </form>
    </div>
</template>
  
<style scoped>
.title {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    padding-bottom: 50px;
    margin-top: 100px;
}

.upload-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    align-items: center;
    margin-top: 50px;
}

.form-group {
    margin-bottom: 15px;
    text-align: center;
}
  
.upload-button {
    background-color: #FF8C00;
    color: white;
    padding: 15px 50px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 18px;
    font-family: 'League Spartan', sans-serif;
}
  
.upload-button:hover {
    background-color: #FF4500;
}
  
input[type="file"] {
    display: none;
}
  
.file-info {
    text-align: center;
    margin-top: 10px;
}

.file-name {
  font-family: 'League Spartan', sans-serif;
}
  
.submit-button {
    display: block;
    padding: 10px 80px;
    justify-self: center;
    margin-top: 30px;
    border: none;
    background-color: #A3A0A0;
    color: white;
    font-size: 17px;
    font-family: 'League Spartan', sans-serif;
    border-radius: 5px;
    cursor: pointer;
}
  
.submit-button:hover {
    background-color: #000;
}

.mensagem {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  font-size: 18px;
  margin-top: 40px;
  color: red;
}
</style>