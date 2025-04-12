<script lang="ts">
import BannerCoordenador from './BannerCoordenador.vue';

export default {
    components: { BannerCoordenador }
}
</script>

<template>
    <BannerCoordenador />
    <h3 class="welcome">Bem-vindo Coordenador!</h3>
</template>

<style scoped>
.welcome {
    text-align: left;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    margin-left: 4rem;
    padding-bottom: 30px;
}
</style>