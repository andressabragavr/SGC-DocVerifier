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
        { title: 'Data de Envio', key: 'submissionDate' },
        { title: 'Horas Atribuídas', key: 'hours' },
        { title: 'Visualizar PDF', key: 'pdfLink' },
        { title: 'Status', key: 'status' }
        ],
        items: [] as {
            title: string;
            activityType: string;
            submissionDate: string;
            hours: number;
            pdfLink: string;
            status: string;
        }[]
    };
  },
  async mounted() {
    try {
      const response = await alunoService.getCertificados();

      this.items = response.data.map((certificado: any) => ({
        title: certificado.titulo,
        activityType: certificado.tipoAtividade,
        submissionDate: new Date(certificado.dataEnvio).toLocaleDateString('pt-BR'),
        hours: certificado.horasAtribuidas,
        pdfLink: certificado.urlPDF,
        status: certificado.status
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
        <v-data-table
        :headers="headers"
        :items="items"
        hide-default-footer
        >
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