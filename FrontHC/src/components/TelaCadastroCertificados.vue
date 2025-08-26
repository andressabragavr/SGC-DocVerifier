<script lang="ts">
import Banner from './Banner.vue';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'TelaCadastroCertificados',
  components: { Banner },

  data() {
    return {
      file: null as File | null,
      fileName: '',
      resultadoIA: null as any,
      isUploading: false,   // 👈 controla o spinner e desabilita botões
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

    async submitForm() {
      if (!this.file) {
        alert('Por favor, selecione um arquivo antes de enviar.');
        return;
      }

      const usuario = JSON.parse(localStorage.getItem('usuario') || '{}');

      const formData = new FormData();
      formData.append('arquivo', this.file);
      formData.append('ra', usuario.ra);

      try {
        this.isUploading = true;

        const res = await fetch('http://localhost:3000/certificados/upload', {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errText = await res.text().catch(() => '');
          throw new Error(errText || 'Falha no upload');
        }

        const data = await res.json();
        this.resultadoIA = data;

        // feedback de sucesso
        alert('Certificado enviado com sucesso!');
        // opcional: resetar seleção após sucesso
        this.file = null;
        this.fileName = '';
        (this.$refs.fileInput as HTMLInputElement).value = '';
      } catch (err) {
        console.error('Erro ao enviar certificado:', err);
        alert('Erro ao enviar certificado');
      } finally {
        this.isUploading = false;
      }
    },
  },
});
</script>

<template>
  <Banner />
  <h1 class="title">Cadastro de Certificados</h1>

  <div class="upload-container" :class="{ 'with-spinner': isUploading }">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="certificate">
          <button
            type="button"
            class="upload-button"
            @click="triggerFileUpload"
            :disabled="isUploading"
          >
            Selecionar arquivo PDF
          </button>
        </label>

        <input
          type="file"
          id="certificate"
          ref="fileInput"
          accept=".pdf"
          @change="handleFileUpload"
          :disabled="isUploading"
          required
        />
      </div>

      <div v-if="fileName" class="file-info">
        <p class="file-name">Arquivo selecionado: {{ fileName }}</p>
      </div>

      <button type="submit" class="submit-button" :disabled="isUploading">
        {{ isUploading ? 'Enviando...' : 'Upload' }}
      </button>

      <!-- Spinner de carregamento -->
      <div v-if="isUploading" class="spinner-wrapper">
        <div class="spinner" aria-label="Carregando"></div>
        <p class="spinner-text">Enviando certificado...</p>
      </div>
    </form>
  </div>
</template>

<style scoped>
.title {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  margin-top: 100px;
  padding-bottom: 50px;
}

.upload-container {
  max-width: 500px;
  margin: 50px auto 0;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, .1);
  transition: margin-bottom 0.3s ease;
}

/* Quando o spinner aparece */
.upload-container.with-spinner {
  margin-bottom: 80px; /* margem extra */
}

.spinner-wrapper {
  margin-top: 30px;
  text-align: center;
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

.upload-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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
  margin: 30px auto 0;
  border: none;
  background-color: #A3A0A0;
  color: white;
  font-size: 17px;
  font-family: 'League Spartan', sans-serif;
  border-radius: 5px;
  cursor: pointer;
}

.submit-button:hover:not(:disabled) {
  background-color: #000;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Spinner */
.spinner-wrapper {
  margin-top: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.spinner {
  border: 6px solid #f3f3f3;     /* cinza claro */
  border-top: 6px solid #FF8C00;  /* laranja */
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 8px;
}

.spinner-text {
  font-family: 'League Spartan', sans-serif;
  font-size: 14px;
  color: #333;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>