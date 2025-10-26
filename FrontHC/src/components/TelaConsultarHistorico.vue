<script lang="ts">
import { defineComponent, ref } from 'vue';
import BannerCoordenador from './BannerCoordenador.vue';
import coordenadorService from '@/services/coordenadorService';

export default defineComponent({
    components: { BannerCoordenador },
    setup() {
        const ra = ref('');
        const isLoading = ref(false);
        const errorMessage = ref('');
        const aluno = ref<any>(null);

        const buscarAluno = async () => {
            if (!ra.value) {
                errorMessage.value = 'Por favor, insira um RA';
                return;
            }

            try {
                isLoading.value = true;
                errorMessage.value = '';
                aluno.value = await coordenadorService.buscarAlunoPorRA(ra.value);
            } catch (error) {
                errorMessage.value = 'Aluno não encontrado ou erro ao buscar dados';
                console.error('Erro na busca:', error);
            } finally {
                isLoading.value = false;
            }
        };

        return {
            ra,
            isLoading,
            errorMessage,
            aluno,
            buscarAluno
        };
    }
});
</script>

<template>
    <BannerCoordenador />
    <main>
        <div class="search-container">
            <input 
                type="text" 
                class="search-input" 
                v-model="ra" 
                placeholder="Buscar por RA..."
                :disabled="isLoading"
            >
            <button 
                class="search-button" 
                @click="buscarAluno"
                :disabled="isLoading"
            >
                {{ isLoading ? 'Buscando...' : 'Buscar' }}
            </button>
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <div v-if="aluno" class="aluno-info">
            <h2>Dados do Aluno</h2>
            <p>Nome: {{ aluno.nome }}</p>
            <p>RA: {{ aluno.ra }}</p>
            <p>Horas Lançadas: {{ aluno.horasLancadas }}</p>
            <p>Horas Faltantes: {{ aluno.horasFaltantes }}</p>
            <p>Horas Exigidas: {{ aluno.horasExigidas }}</p>

            <h3>Certificados</h3>
            <div class="certificados-lista">
                <div v-for="cert in aluno.certificados" :key="cert.id" class="certificado-item">
                    <h4>{{ cert.titulo }}</h4>
                    <p>Categoria: {{ cert.categoria }}</p>
                    <p>Tipo: {{ cert.tipoAtividade }}</p>
                    <p>Data: {{ cert.dataEnvio }}</p>
                    <p>Horas: {{ cert.horas }}</p>
                    <!-- <p>Status: {{ cert.status }}</p> -->
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
.search-container { 
    display: flex; 
    justify-content: center; 
    margin-top: 80px; 
} 

.search-input { 
    padding: 15px; 
    width: 300px; 
    border: 1px solid #ccc; 
    border-radius: 5px 0 0 5px; 
    font-family: 'League Spartan', sans-serif;
    font-size: 16px;
    font-weight: bold;
    color: #000;
    border-color: #FF8C00;
} 

.search-button { 
    padding: 10px; 
    border: 1px solid #ccc; 
    border-radius: 0 5px 5px 0; 
    background-color: #FF8C00; 
    color: white; cursor: pointer; 
    font-family: 'League Spartan', sans-serif;
    font-size: 16px;
    font-weight: bold;
} 

.search-button:hover { 
    background-color: #FF4500; 
}
</style>