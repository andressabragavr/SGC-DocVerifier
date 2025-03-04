<script lang="ts">
import Banner from './Banner.vue';

export default {
    components: { Banner }
}
</script> 

<template>
    <Banner />
    <main>
        <h3 class="welcome">Bem-vindo {fullName}!</h3>
        <div class="itemsContainer">
            <div>
                <h2 class="titles">Certificados Cadastrados</h2>
                <h1 class="titles">2</h1>
            </div>
            <div>
                <h2 class="titles">Horas Lançadas</h2>
                <h1 class="titles">37</h1>
            </div>
            <div>
                <h2 class="titles">Horas Faltantes</h2>
                <h1 class="titles">163</h1>
            </div>
            <div>
                <h2 class="titles">Horas Exigidas</h2>
                <h1 class="titles">200</h1>
            </div>
        </div>
    </main>
</template>

<style scoped>
.welcome {
    text-align: left;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    margin-left: 4rem;
    padding-bottom: 30px;
}

.itemsContainer {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
}

.titles {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
}
</style>