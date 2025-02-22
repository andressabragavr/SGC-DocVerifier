<script lang="ts">
import BannerCoordenador from './BannerCoordenador.vue';

export default {
    components: { BannerCoordenador }
}

// function search() {
//     var query = document.getElementById("search-input").value;
// }
</script>

<template>
    <BannerCoordenador />
    <main>
        <h3 class="welcome">Bem-vindo Andréa!</h3>
        <div class="search-container">
            <input type="text" class="search-input" id="search-input" placeholder="Buscar por RA...">
            <button class="search-button" onclick="search()">Buscar</button>
        </div>
    </main>
</template>

<style scoped>
.welcome {
    text-align: left;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-top: 4rem;
    margin-left: 4rem;
    padding-bottom: 30px;
}

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
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 16px;
    font-weight: bold;
} 

.search-button:hover { 
    background-color: #FF4500; 
}
</style>