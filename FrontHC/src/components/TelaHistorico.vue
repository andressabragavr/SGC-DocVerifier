<script lang="ts">
import Banner from './Banner.vue';

export default {
    components: { Banner }
}
</script> 

<template>
    <Banner />
    <main>
        <h1 class="title">Histórico</h1>
        <div class="subTitlesContainer">
            <h3 class="subTitles">Título</h3>
            <!-- <div class="items-container"> -->
                <h3 class="subTitles">Categoria</h3>
                <h3 class="subTitles">Tipo de Atividade</h3>
            <!-- </div>
            <div class="items-container"> -->
                
                <h3 class="subTitles">Data de Envio</h3>
            <!-- </div> -->
            <!-- <div class="items-container"> -->
                <h3 class="subTitles">Horas Atribuídas</h3>
            <!-- </div> -->
            <!-- <div class="items-container"> -->
                <h3 class="subTitles">Visualizar PDF</h3>
            <!-- </div> -->
        </div>
        <hr class="separator-line">
        <div class="items-container">
            <div class="items-container">
                <p class="list-item">oi</p>
            </div>
            <div class="items-container">
                <p class="list-item">oi</p>
            </div>
            <div class="items-container">
                <p class="list-item">oi</p>
            </div>
            <div class="items-container">
                <p class="list-item">oi</p>
            </div>
            <div class="items-container">
                <p class="list-item">oi</p>
            </div>
        </div>
    </main>
</template>

<style scoped>
.title {
    text-align: center;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-top: 4rem;
    padding-bottom: 30px;
}

.subTitlesContainer {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
}

.items-container {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    /* text-align: center; */
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
</style>