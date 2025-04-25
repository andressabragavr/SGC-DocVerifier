<script lang="ts">
import { defineComponent } from 'vue';
import alunoService from '../services/alunoService';
import Banner from './Banner.vue';

export default defineComponent({
    components: { Banner },
    data() {
        return {
            items: [
                // { 
                //     title: 'Phyton para Iniciantes', 
                //     category: 'Livre', 
                //     activityType: 'Cursos de Formação Complementar (fora da IES)', 
                //     submissionDate: '01/03/2023', 
                //     hours: '20', 
                //     pdfLink: 'link',
                //     status: 'Aprovado',
                // },
                // { 
                //     title: 'JavaScript Avançado', 
                //     category: 'Livre', 
                //     activityType: 'Cursos de Formação Complementar (fora da IES)', 
                //     submissionDate: '20/04/2024', 
                //     hours: '15', 
                //     pdfLink: 'link',
                //     status: 'Pendente',
                // },
            ]
        };
    },
    // async mounted() {
    //     try {
    //         const response = await alunoService.getCertificados();
    //         this.items = response.map(certificado => ({
    //             title: certificado.nome,
    //             category: certificado.categoria,
    //             activityType: certificado.tipoAtividade,
    //             submissionDate: new Date(certificado.dataEnvio).toLocaleDateString('pt-BR'),
    //             hours: certificado.horasAtribuidas,
    //             pdfLink: certificado.urlPDF,
    //             status: certificado.status
    //         }));
    //     } catch (error) {
    //         console.error('Erro ao carregar certificados:', error);
    //     }
    // }
});
</script>

<template>
    <Banner />
    <main>
        <h1 class="title">Histórico</h1>
        <hr class="separator-line">
        <v-data-table 
            :headers="[
                { title: 'Título', key: 'title' },
                { title: 'Categoria', key: 'category' },
                { title: 'Tipo de Atividade', key: 'activityType' },
                { title: 'Data de Envio', key: 'submissionDate' },
                { title: 'Horas Atribuídas', key: 'hours' },
                { title: 'Visualizar PDF', key: 'pdfLink' },
                { title: 'Status', key: 'status' }
            ]"
            :items="items" 
            hide-default-footer
        ></v-data-table>
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
</style>