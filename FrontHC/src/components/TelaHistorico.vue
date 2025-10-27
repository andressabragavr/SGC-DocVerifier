<script lang="ts">
import { defineComponent } from 'vue';
import alunoService from '../services/alunoService';
import Banner from './Banner.vue';

export default defineComponent({
  components: { Banner },
  data() {
    return {
        headers: [
        { title: 'Título', key: 'title'},
        { title: 'Tipo de Atividade', key: 'activityType' },
        { title: 'Data de Conclusão', key: 'conclusionDate' },
        { title: 'Data de Envio', key: 'submissionDate' },
        { title: 'Horas Atribuídas', key: 'hours' },
        { title: 'Visualizar PDF', key: 'pdfLink' }
        ],
        items: [] as {
            title: string;
            activityType: string;
            conclusionDate: string;
            submissionDate: string;
            hours: number;
            pdfLink: string;
        }[]
    };
  },
  methods: {
    // Corrige textos que vieram com encoding latin1/utf-8 trocado (mojibake)
    fixMojibake(s: any): string {
      const str = String(s ?? '');
      try {
        return decodeURIComponent(escape(str));
      } catch {
        return str;
      }
    }
  },
  async mounted() {
    try {
      const response = await alunoService.getCertificados();

      this.items = response.data.map((certificado: any) => ({
        title: this.fixMojibake(certificado.titulo),
        activityType: this.fixMojibake(certificado.tipoAtividade),
        submissionDate: certificado.dataEnvio ? new Date(certificado.dataEnvio).toLocaleDateString('pt-BR') : '—',
        conclusionDate: certificado.dataConclusao ? new Date(certificado.dataConclusao).toLocaleDateString('pt-BR') : '—',                                  
        hours: Number(certificado.horasAtribuidas || 0),
        pdfLink: certificado.urlPDF
      }));
    } catch (error) {
      console.error('Erro ao carregar certificados:', error);
    }
  }
});
</script>


<template>
    <Banner />
    <main>
        <h1 class="title">Histórico</h1>
        <hr class="separator-line">
        <v-data-table :headers="headers" :items="items" hide-default-footer>
        <template #item.pdfLink="{ item }">
            <a :href="item.pdfLink" target="_blank" rel="noopener noreferrer">
            <button class="view-pdf-button">Abrir PDF</button>
            </a>
        </template>
        </v-data-table>
    </main>
</template>

<style scoped>
.title {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    padding-bottom: 30px;
}

:deep(.v-data-table-header th) {
    font-weight: bold !important;
    /* font-size: 60px !important; */
}

.separator-line {
    width: 100%;
    height: 2px;
    background-color: #A3A0A0;
    margin: 20px 0;
    border: none;
}

.view-pdf-button {
  background-color: #FF8C00;
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'League Spartan', sans-serif;
  font-weight: bold;
}

.view-pdf-button:hover {
  background-color: #FF4500;
}

:deep(th) {
  font-weight: bold !important;
}
</style>