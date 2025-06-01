<script lang="ts">
import BannerCoordenador from './BannerCoordenador.vue';
import axios from 'axios';

export default {
  components: { BannerCoordenador },
  data() {
    return {
      isDropdownOpen: false,
      selectedOption: 'Procurar por ...',
      searchQuery: '',
      options: ['RA', 'Nome do Aluno', 'Tipo de Atividade', 'Título'],
      items: [],
      alunoInfo: null as null | { ra: string; name: string; curso: string },
      nenhumResultado: false,

    };
  },
  methods: {
    toggleDropdown() {
      this.isDropdownOpen = !this.isDropdownOpen;
    },
    selectOption(option: string) {
      this.selectedOption = option;
      this.isDropdownOpen = false;
    },
    async buscar() {
        if (!this.searchQuery || this.selectedOption === 'Procurar por ...') {
            alert('Selecione uma opção e preencha a busca.');
            return;
        }

        const campoMap: Record<string, string> = {
            'RA': 'ra',
            'Nome do Aluno': 'name',
            'Tipo de Atividade': 'tipoAtividade',
            'Título': 'titulo'
        };

        const filtro = campoMap[this.selectedOption];
        try {
            const res = await axios.get(`http://localhost:3000/certificados/busca`, {
            params: { filtro, valor: this.searchQuery }
            });
            this.items = res.data.certificados;
            this.alunoInfo = res.data.usuario;
            this.nenhumResultado = false;
        } catch (error) {
            this.items = [];
            this.alunoInfo = null;
            this.nenhumResultado = true;
        }
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
      <button class="search-button" @click="buscar">Buscar</button>
    </div>
  </div>

  <div class="mensagem-container" v-if="nenhumResultado">
    <p class="mensagem-vazia">Nenhum resultado encontrado para "{{ searchQuery }}".</p>
  </div>

  <div v-if="alunoInfo" class="info">
    <p>RA: {{ alunoInfo.ra }}</p>
    <p>Nome do Aluno: {{ alunoInfo.name }}</p>
    <p>Curso: {{ alunoInfo.curso }}</p>
  </div>

  <div class="table-container" v-if="items.length">
    <v-data-table 
      :headers="[
        { title: 'Título', key: 'titulo' },
        { title: 'Categoria', key: 'categoria' },
        { title: 'Tipo de Atividade', key: 'tipoAtividade' },
        { title: 'Data de Envio', key: 'dataEnvio' },
        { title: 'Horas Atribuídas', key: 'horasAtribuidas' },
        { title: 'Visualizar PDF', key: 'urlPDF' },
      ]"
      :items="items" 
      hide-default-footer
    ></v-data-table>
  </div>
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

.mensagem-container {
  width: 100%;
  text-align: center;
  margin-top: 15px;
}

.mensagem-vazia {
  color: #a00;
  font-size: 16px;
  font-family: 'League Spartan', sans-serif;
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