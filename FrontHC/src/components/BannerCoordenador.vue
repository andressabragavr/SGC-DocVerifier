<script lang="ts">
import { defineComponent } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
    name: 'menuOptions',
    setup() {
        const route = useRoute();

        const isActive = (path: string): boolean => {
            return route.path === path;
        }

        return {
            isActive
        }
    }
})
</script>

<template>
    <header class="banner">
        <div class="logo">
            <img src="../assets/LogoFacens.png" alt="Logo" class="logo">
        </div>
        <div class="menu">
            <nav class="menuOptions">
            <router-link to="/TelaConsultarHistorico" class="menu-item" :class="{ 'active': isActive('/TelaConsultarHistorico') }">Consultar Histórico</router-link>
            <router-link to="/TelaRelatorio" class="menu-item" :class="{ 'active': isActive('/TelaRelatorio') }">Gerar Relatório</router-link>
            <router-link to="/TelaValidarAtividades" class="menu-item" :class="{ 'active': isActive('/TelaValidarAtividades') }">Validar Atividades</router-link>
        </nav>
        </div>
    </header>
</template>

<style scoped>
.banner {
    background-color: #008B8B;
    padding: 0.8rem 0.5rem;
    width: 100%;
    justify-content: space-between;
    display: flex;
}

.logo {
    height: 4.5rem;
    margin-bottom: 2rem;
    margin-top: 0.6rem;
    margin-left: 0.3rem;
}

.menu {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
}

.menuOptions {
    background-color: #008B8B;
    padding: 1rem;
    display: flex;
    gap: 2rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: bold;
    font-size:larger;
}

.menu-item {
    color: #FFF;
    text-decoration: none;
    padding-bottom: 0.5 rem;
    position: relative;
}

.menu-item::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background-color: #FFF;
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.menu-item:hover::after, .menu-item.active::after {
    transform: scaleX(1);
}


@media only screen and (max-width: 1300px) {
  .banner {
    padding: 0.8rem 0.5rem;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
  }
}

@media only screen and (max-width: 767px) {
  .banner {
    padding: 0.8rem 0.5rem;
  }

}
</style>