<script lang="ts">
import { defineComponent } from 'vue';
import Banner from './Banner.vue';

export default defineComponent({
    components: { Banner },
    data() {
        return {
            items: [
                { 
                    title: 'Phyton para Iniciantes', 
                    category: 'Livre', 
                    activityType: 'Cursos de Formação Complementar (fora da IES)', 
                    submissionDate: '20', 
                    hours: '20', 
                    pdfLink: 'link' 
                },
            ]
        };
    }
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
                { title: 'Visualizar PDF', key: 'pdfLink' }
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