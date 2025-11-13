<script lang="ts">
import Banner from './Banner.vue';
import { defineComponent, computed } from 'vue';

type BackendAdjustResponse = {
  message: string;
  needsInfo: boolean;
  requiredFields: string[];
  certificadoId: string;
};

export default defineComponent({
  name: 'TelaCadastroCertificados',
  components: { Banner },

  data() {
    return {
      // upload
      file: null as File | null,
      fileName: '',
      isUploading: false,

      // estado do fluxo
      hasSubmitted: false,          // esconde upload após primeira submissão
      notificacao: '' as string,    // mensagem principal (sucesso/erro/ajustar)
      notificacaoType: '' as 'success' | 'error' | 'info' | '',

      // ajuste
      needsInfo: false,
      requiredFields: [] as string[],
      certificadoId: '' as string,
      complementoText: '' as string,
      isCompleting: false,          // spinner do complemento
    };
  },

  computed: {
    // remove duplicatas (ex.: “data de conclusão” repetido)
    requiredFieldsUnique(): string[] {
      return Array.from(new Set(this.requiredFields.map(f => (f || '').trim().toLowerCase())));
    },

    // mensagem “lista” na mesma linha, sem duplicar
    requiredFieldsInline(): string {
      return this.requiredFieldsUnique.join(', ');
    }
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

    // --- utils p/ interpretar o texto do usuário e mapear p/ backend ---
    parseDateToISO(s: string): string | null {
      const t = s.trim();
      // dd/mm/yyyy
      const br = t.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
      if (br) {
        const d = br[1].padStart(2, '0');
        const m = br[2].padStart(2, '0');
        const y = br[3];
        return `${y}-${m}-${d}`;
      }
      // yyyy-mm-dd
      const iso = t.match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if (iso) return t;
      return null;
    },

    parseHoursToInt(s: string): number | null {
      const m = s.match(/(\d{1,3})/);
      if (!m) return null;
      return parseInt(m[1], 10);
    },

    // Mapeia rótulos → chaves do backend
    labelToKey(label: string): string | null {
      const L = label.trim().toLowerCase();
      if (L.includes('data')) return 'dataConclusao';
      if (L.includes('carga') || L.includes('hora')) return 'horasAtribuidas';
      if (L.includes('nome')) return 'nomeNoCertificado';
      if (L.includes('institu')) return 'instituicao';
      if (L.includes('título') || L.includes('curso')) return 'titulo';
      return null;
    },

    buildComplementoObject(text: string): Record<string, any> {
      // Estratégia simples:
      // - Se só há 1 campo faltante, usa o texto inteiro para aquele campo.
      // - Se há >1, tenta pares "campo: valor" por linha. Ex.: "data: 30/04/2024"
      const complemento: Record<string, any> = {};
      const missing = this.requiredFieldsUnique;

      if (missing.length <= 1) {
        const key = this.labelToKey(missing[0] || '') || 'observacao';
        const val = text.trim();

        if (key === 'dataConclusao') {
          const iso = this.parseDateToISO(val);
          if (iso) complemento[key] = iso;
        } else if (key === 'horasAtribuidas') {
          const h = this.parseHoursToInt(val);
          if (h != null) complemento[key] = h;
        } else if (key === 'observacao') {
          complemento[key] = val;
        } else {
          complemento[key] = val;
        }
        return complemento;
      }

      // múltiplos campos: aceita linhas do tipo "campo: valor"
      const lines = text.split(/\n+/).map(l => l.trim()).filter(Boolean);
      for (const ln of lines) {
        const parts = ln.split(':');
        if (parts.length < 2) continue;
        const fieldLabel = parts[0].trim().toLowerCase();
        const value = parts.slice(1).join(':').trim();

        const key = this.labelToKey(fieldLabel);
        if (!key) continue;

        if (key === 'dataConclusao') {
          const iso = this.parseDateToISO(value);
          if (iso) complemento[key] = iso;
        } else if (key === 'horasAtribuidas') {
          const h = this.parseHoursToInt(value);
          if (h != null) complemento[key] = h;
        } else {
          complemento[key] = value;
        }
      }
      return complemento;
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

        const data = await res.json().catch(() => ({} as any));

        // SUCESSO (201)
        if (res.status === 201) {
          // limpa input de arquivo com segurança
          const fileInput = this.$refs.fileInput as HTMLInputElement | null;
          if (fileInput) {
            fileInput.value = '';
          }

          this.file = null;
          this.fileName = '';

          this.notificacao = '✅ Certificado cadastrado com sucesso!';
          this.notificacaoType = 'success';
          this.needsInfo = false;
          this.requiredFields = [];
          this.certificadoId = '';
          this.complementoText = '';
          this.hasSubmitted = true; // esconde upload depois do sucesso
          return;
        }

        // AJUSTAR (202)
        if (res.status === 202 && data.needsInfo) {
          this.notificacao = '📝 As seguintes informações são necessárias para o cadastro do certificado.';
          this.notificacaoType = 'info';
          this.needsInfo = true;
          this.requiredFields = data.requiredFields || [];
          this.certificadoId = data.certificadoId || '';
          this.hasSubmitted = true; // mostra card de complemento
          return;
        }

        // ERROS (400/409/500)
        const rawMsg = (data.error || data.message || '').toString();

        if (rawMsg.includes('duplicata forte') || rawMsg.includes('já enviado anteriormente')) {
          this.notificacao = '⚠️ Este certificado já foi enviado anteriormente.';
          this.notificacaoType = 'error';
        } else {
          this.notificacao = rawMsg || '❌ Não foi possível cadastrar o certificado.';
          this.notificacaoType = 'error';
        }

        // em caso de erro, NÃO marcamos hasSubmitted = true,
        // para o usuário poder tentar reenviar
        this.hasSubmitted = false;
      } catch (err) {
        console.error('Erro ao enviar certificado:', err);
        this.notificacao = 'Erro ao enviar certificado.';
        this.notificacaoType = 'error';
        this.hasSubmitted = false;
      } finally {
        this.isUploading = false;
      }
    },

    async enviarComplemento() {
      if (!this.certificadoId) {
        alert('Operação inválida: id do certificado ausente.');
        return;
      }
      const complemento = this.buildComplementoObject(this.complementoText);
      if (!Object.keys(complemento).length) {
        alert('Insira os dados solicitados.');
        return;
      }

      try {
        this.isCompleting = true;
        const res = await fetch(`http://localhost:3000/certificados/${this.certificadoId}/complementar`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ complemento })
        });
        const data = await res.json().catch(() => ({} as any));

        if (res.status === 200) {
          this.notificacao = '✅ Certificado cadastrado com sucesso!';
          this.notificacaoType = 'success';
          this.needsInfo = false;
          this.requiredFields = [];
          this.complementoText = '';
          this.certificadoId = '';
          return;
        }

        if (res.status === 202 && data.needsInfo) {
          this.notificacao = '📝 Ainda faltam informações.';
          this.notificacaoType = 'info';
          this.requiredFields = data.requiredFields || [];
          this.complementoText = '';
          return;
        }

        this.notificacao = data.message || '❌ Não foi possível concluir o cadastro.';
        this.notificacaoType = 'error';
      } catch (err) {
        console.error('Erro ao complementar informações:', err);
        this.notificacao = 'Erro ao complementar informações.';
      } finally {
        this.isCompleting = false;
      }
    },

    dedupFields(fields: string[]): string[] {
      return Array.from(
        new Set<string>(
          (fields ?? []).map((f: string) => (f ?? '').trim().toLowerCase())
        )
      );
    }
  },
});
</script>

<template>
  <Banner />
  <h1 class="title">Cadastro de Certificados</h1>

  <div
    class="upload-container"
    :class="{ 'with-spinner': isUploading || isCompleting }"
  >
    <br />

    <!-- 1) FORM DE UPLOAD (some depois do 1º envio OU enquanto está enviando) -->
    <form
      @submit.prevent="submitForm"
      v-if="!hasSubmitted && !isUploading"
    >
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

        <br /><br />

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
        <p class="file-name">
          Arquivo selecionado: <strong>{{ fileName }}</strong>
        </p>
      </div>

      <br />

      <!-- botão some quando isUploading=true -->
      <button
        type="submit"
        class="submit-button"
        :disabled="isUploading || !file"
      >
        Enviar
      </button>
      <br />
    </form>

    <!-- Mensagem principal -->
    <div
      v-if="notificacao"
      class="notice"
      :class="`notice--${notificacaoType || (notificacao.startsWith('✅') ? 'success' : 'info')}`"
      role="alert"
    >
      {{ notificacao }}
    </div>

    <!-- 2) CARD DE COMPLEMENTO (só aparece depois do 1º upload) -->
    <div v-if="hasSubmitted && needsInfo" class="complement-card">
      <h4>Informações faltantes:</h4>
      <ul class="missing-list">
        <li v-for="f in requiredFieldsUnique" :key="f">• {{ f }}</li>
      </ul>

      <textarea
        v-model="complementoText"
        class="complement-input"
        placeholder="Insira aqui as informações solicitadas"
        :disabled="isCompleting"
      ></textarea>

      <!-- botão some enquanto está completando -->
      <button
        v-if="!isCompleting"
        class="submit-button"
        @click="enviarComplemento"
        :disabled="!complementoText.trim()"
      >
        Enviar informações
      </button>
    </div>

    <!-- 3) SPINNER GLOBAL (aparece nos DOIS momentos) -->
    <div v-if="isUploading || isCompleting" class="spinner-wrapper">
      <div class="spinner" aria-label="Carregando"></div>
      <p class="spinner-text">
        {{
          isCompleting
            ? 'Enviando complementação...'
            : 'Cadastrando certificado...'
        }}
      </p>
    </div>
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

.upload-container.with-spinner {
  margin-bottom: 80px;
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

.upload-button:hover { background-color: #FF4500; }
.upload-button:disabled { opacity: 0.7; cursor: not-allowed; }

input[type="file"] { display: none; }

.file-info { 
  text-align: center; 
  margin-top: 10px; 
}

.file-name {
  font-family: 'League Spartan', sans-serif;
  font-weight: normal; 
}

.file-name strong {
  font-weight: bold; 
  color: rgb(56, 128, 252);
}

.submit-button {
  display: block;
  padding: 10px 80px;
  margin: 20px auto 0;
  border: none;
  background-color: #333;
  color: white;
  font-size: 17px;
  font-family: 'League Spartan', sans-serif;
  border-radius: 5px;
  cursor: pointer;
}

.submit-button:hover:not(:disabled) { background-color: #000; }
.submit-button:disabled { opacity: 0.7; cursor: not-allowed; }

.notice {
  margin: 12px 4px 0;
  padding: 12px 16px;
  border-radius: 10px;
  font-family: 'League Spartan', sans-serif;
  text-align: center;
  border: 1px solid transparent;
  box-shadow: 0 1px 2px rgba(0,0,0,.06);
}

/* Sucesso */
.notice--success {
  background: #e8f7ee;
  color: #14532d;
  border-color: green;
  font-size: 19px;
}

/* Informação */
.notice--info {
  background: #eef6ff;
  color: #0b3c74;
  border-color: rgb(0, 73, 156);
  font-size: 19px;
}

/* Erro */
.notice--error {
  background: #fdecec;
  color: #7a1a1a;
  border-color: red;
  font-size: 19px;
}

.complement-card {
  margin-top: 14px;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
}

.missing-list {
  list-style: none;
  padding-left: 0;
  margin: 0 0 10px 0;
  font-family: 'League Spartan', sans-serif;
}
.missing-list li { margin-left: 8px; }

.complement-input {
  width: 100%;
  min-height: 90px;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
  font-family: 'League Spartan', sans-serif;
  margin-top: 8px;
}

.spinner-wrapper {
  margin-top: 14px;
  text-align: center;
  margin-bottom: 6px;
}
.spinner {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #FF8C00;
  border-radius: 50%;
  width: 40px; height: 40px;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 8px;
}
.spinner-text {
  font-family: 'League Spartan', sans-serif;
  font-size: 18px;
  color: #333;
  margin-top: 5px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
