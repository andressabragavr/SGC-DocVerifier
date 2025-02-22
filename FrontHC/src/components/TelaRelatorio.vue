<script lang="ts">
import BannerCoordenador from './BannerCoordenador.vue';

export default {
    components: { BannerCoordenador }
}
</script>

<template>
    <BannerCoordenador />
    <main>
        <div class="search">
            <div class="search-container">
                <input type="text" class="search-input" id="search-input" placeholder="Buscar por Certificado...">
                <button class="search-button" onclick="search()">Buscar</button>
            </div>
            <div class="search-container">
                <input type="text" class="search-input" id="search-input" placeholder="Buscar por Horas...">
                <button class="search-button" onclick="search()">Buscar</button>
            </div>
        </div>
        <h1 class="title">Certificados de Python</h1>
        <div class="subTitlesContainer">
            <div>
                <h3 class="subTitles">RA</h3>
            </div>
            <div>
                <h3 class="subTitles">Nome do Aluno</h3>
            </div>
            <div>
                <h3 class="subTitles">Curso</h3>
            </div>
            <div>
                <h3 class="subTitles">Visualizar PDF</h3>
            </div>
        </div>
        <hr class="separator-line">
    </main>
    <v-container>
    <v-text-field v-model="search" label="Search Name" clearable></v-text-field>
    <v-slider v-model="minAge" label="Minimum Age" min="0" max="40"></v-slider>

    <v-list>
      <v-list-item v-for="item in filteredItems" :key="item.name">
        {{ item.name }} ({{ item.age }} years old)
      </v-list-item>
    </v-list>
  </v-container>
</template>

<style scoped>
.search {
    display: flex;
    justify-content: space-around;
    flex-direction: row;
}

.search-container { 
    display: flex; 
    justify-content: center; 
    margin-top: 60px; 
} 

.search-input { 
    padding: 12px; 
    width: 300px; 
    border: 1px solid #ccc; 
    border-radius: 5px 0 0 5px; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 15px;
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
    /* font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; */
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    font-weight: bold;
} 

.search-button:hover { 
    background-color: #FF4500; 
}

.title {
    text-align: center;
    /* font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; */
    /* font-family:'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif; */
    font-family: "League Spartan", serif;
    margin-top: 5rem;
    margin-bottom: 3rem;
}

.subTitlesContainer {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
}

.subTitles {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #A3A0A0;
}

.separator-line {
    width: 100%;
    height: 2px;
    background-color: #A3A0A0;
    margin: 20px 0;
    border: none;
}

@media only screen and (max-width: 1300px) {
  .search {
    display: flex;
    justify-content: space-around;
    flex-direction: colunm;
    }
}

@media only screen and (max-width: 767px) {
  .search {
    display: flex;
    justify-content: space-around;
    flex-direction: column;
  }

}
</style>