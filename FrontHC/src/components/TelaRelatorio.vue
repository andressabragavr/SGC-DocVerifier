<script lang="ts">
import BannerCoordenador from './BannerCoordenador.vue';

export default {
    components: { BannerCoordenador },
    data() {
        return {
            isDropdownOpen: false,
            selectedOption: 'Procurar por ...',
            searchQuery: '',
            options: [
                'RA',
                'Nome do Aluno',
                'Tipo de Atividade',
                'Título',
            ],
            items: [
                {
                    title: 'Python para Iniciantes',
                    category: 'Livre',
                    activityType: 'Curso de Extensão',
                    submissionDate: '20/04/2024',
                    hours: 20,
                    pdfLink: 'documento1.pdf',
                },
                {
                    title: 'JavaScript Avançado',
                    category: 'Livre',
                    activityType: 'Curso de Extensão',
                    submissionDate: '10/04/2024',
                    hours: 15,
                    pdfLink: 'documento2.pdf',
                },
                {
                    title: 'Technische - Hochschule Ingolstadt',
                    category: 'Livre',
                    activityType: 'Intercâmbio',
                    submissionDate: '22/02/2024',
                    hours: 40,
                    pdfLink: 'documento3.pdf',
                },
                {
                    title: 'Making Roads Safer: A Vehicle Blind Spot Alert System Co-Design With End-Users',
                    category: 'Obrigatória',
                    activityType: 'Artigo Científico',
                    submissionDate: '20/10/2023',
                    hours: 40,
                    pdfLink: 'documento4.pdf',
                },
            ]
        }
    },
    methods: {
        toggleDropdown() {
            this.isDropdownOpen = !this.isDropdownOpen
        },
        selectOption(option: string) {
            this.selectedOption = option
            this.isDropdownOpen = false
        }
    }
};
</script>

<template>
    <BannerCoordenador />
    <div class="search-container">
        <div class="dropdown-wrapper">
            <button class="dropdown-button" @click="toggleDropdown">
                {{ selectedOption }}
                <span class="dropdown-arrow">▼</span>
            </button>
            <div v-if="isDropdownOpen" class="dropdown-menu">
                <div
                    v-for="(option, index) in options"
                    :key="index"
                    class="dropdown-item"
                    @click="selectOption(option)"
                >
                    {{ option }}
                </div>
            </div>
        </div>
        <div class="search-bar">
            <input 
                type="text" 
                v-model="searchQuery"
                placeholder="Digite sua busca..."
                class="search-input"
            >
            <button class="search-button">Buscar</button>
        </div>
    </div>
    <!-- <div class="info">
        <p>RA: 210331</p>
        <p>Nome do Aluno: Pedro Henrique Lisboa</p>
        <p>Curso: Engenharia da Computação</p>
    </div>
    <div class="table-container">
        <v-data-table 
            :headers="[
                { title: 'Título', key: 'title' },
                { title: 'Categoria', key: 'category' },
                { title: 'Tipo de Atividade', key: 'activityType' },
                { title: 'Data de Envio', key: 'submissionDate' },
                { title: 'Horas Atribuídas', key: 'hours' },
                { title: 'Visualizar PDF', key: 'pdfLink' },
            ]"
            :items="items" 
            hide-default-footer
        ></v-data-table>
    </div>
    <img src="../assets/grafico_barra.jpeg" class="graph" /> -->
</template>

<style scoped>
.search-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 20px auto;
    margin-top: 60px;
    max-width: 800px;
}

.dropdown-wrapper {
    position: relative;
    width: 200px;
}

.dropdown-button {
    width: 100%;
    padding: 10px;
    background-color: #FF8C00;
    color: white;
    border: 1px solid #ddd;
    border-radius: 4px 0 0 4px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dropdown-arrow {
    font-size: 12px;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    background-color: #eeeeee;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.dropdown-item {
    padding: 10px;
    cursor: pointer;
}

.dropdown-item:hover {
    background-color: #f5f5f5;
}

.search-bar {
    display: flex;
    flex-grow: 1;
    max-width: 500px;
}

.search-input {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 0;
    font-size: 14px;
    min-width: 300px;
    border-left: none;
}

.search-button {
    padding: 10px 20px;
    background-color: #FF8C00;
    color: white;
    border: 1px solid #ddd;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    white-space: nowrap;
    border-left: none;
}

.search-button:hover {
    background-color: #FF7F00;
}

.table-container {
    margin: 20px auto;
    max-width: 1200px;
    padding: 0 20px;
}

.info {
    text-align: left;
    font-family: 'League Spartan', sans-serif;
    margin-top: 80px;
    margin-left: 200px;
}

.graph {
    margin-top: 50px;
    margin-left: 450px;
    /* max-width: 100%;
    height: auto; */
}

:deep(.v-data-table) {
    font-size: 16px;  
}

:deep(.v-data-table-header) {
    font-size: 19px;  /* Larger headers */
    font-weight: bold;  /* Bold headers */
}

@media only screen and (max-width: 1300px) {
    .search-container {
        flex-direction: column;
        align-items: stretch;
        margin: 20px auto;
        padding: 0 20px;
    }

    .dropdown-wrapper {
        width: 100%;
    }

    .dropdown-button {
        border-radius: 4px 4px 0 0;
    }

    .search-bar {
        max-width: 100%;
    }

    .search-input {
        min-width: 0;
        border-radius: 0;
        border-left: 1px solid #ddd;
        border-top: none;
    }

    .search-button {
        border-radius: 0 0 4px 4px;
        border-left: 1px solid #ddd;
        border-top: none;
    }
}

@media only screen and (max-width: 767px) {
    .search-container {
        margin: 10px auto;
        padding: 0 10px;
    }

    .search-bar {
        flex-direction: column;
    }

    .search-input {
        border-radius: 0;
        border: 1px solid #ddd;
    }

    .search-button {
        width: 100%;
        border-radius: 0 0 4px 4px;
        border: 1px solid #ddd;
        border-top: none;
    }
}
</style>