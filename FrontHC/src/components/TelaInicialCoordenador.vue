<script setup lang="ts">
import { ref, onMounted } from 'vue';
import BannerCoordenador from './BannerCoordenador.vue';

type Indicador = {
  tipoAtividade: string;
  count: number;
};

const indicadores = ref<Indicador[]>([]);
const errorMsg = ref('');
const isLoading = ref(false);

async function carregarIndicadores() {
  try {
    isLoading.value = true;
    errorMsg.value = '';

    const res = await fetch('http://localhost:3000/indicadores/tipos');
    if (!res.ok) {
      throw new Error('HTTP ' + res.status);
    }

    const json = await res.json();
    indicadores.value = Array.isArray(json.data) ? json.data : [];
  } catch (err) {
    console.error('Erro ao carregar indicadores:', err);
    errorMsg.value = 'Erro ao carregar indicadores.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  carregarIndicadores();
});
</script>

<template>
    <BannerCoordenador />
    <h3 class="welcome">Bem-vindo Coordenador!</h3>

    <section class="dashboard">
    <h3 class="title">Visão geral dos certificados cadastrados pelos alunos.</h3>
    <p class="subtitle">
      Abaixo você encontra a quantidade de certificados aceitos em cada tipo de atividade.
    </p>

    <p v-if="isLoading" class="loading">Carregando indicadores...</p>
    <p v-else-if="errorMsg" class="error">{{ errorMsg }}</p>

    <div v-else class="cards-grid">
      <div
        v-for="ind in indicadores"
        :key="ind.tipoAtividade"
        class="card"
      >
        <div class="card-pill">
          {{ ind.tipoAtividade }}
        </div>
        <div class="card-number">
          {{ ind.count }}
        </div>
        <p class="card-footer">
          certificados cadastrados
        </p>
      </div>

      <!-- Caso venha vazio por algum motivo -->
      <p v-if="!indicadores.length" class="empty">
        Ainda não há certificados aceitos para exibir aqui.
      </p>
    </div>
  </section>
</template>

<style scoped>
.welcome {
    text-align: left;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    margin-left: 4rem;
    padding-bottom: 30px;
}

.dashboard {
  max-width: 1100px;
  margin: 40px auto 60px;
  padding: 0 24px;
}

.title {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  font-size: 28px; /* 🔹 menor */
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  font-size: 15px;
  color: #555;
  margin-bottom: 40px;
  margin-top: 30px;
}

.loading,
.error,
.empty {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  margin-top: 20px;
}

.loading {
  color: #555;
}

.error {
  color: #e53935;
}

.empty {
  color: #777;
}

/* ==== GRID DE CARDS ==== */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 🔹 força 3 colunas fixas */
  gap: 26px 30px; /* espaço entre cards */
  justify-items: center;
  align-items: stretch;
  margin-top: 20px;
}

@media (max-width: 900px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

/* ==== CARD ==== */
.card {
  width: 280px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 20px 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.12);
}

/* ==== PÍLULA DO TÍTULO ==== */
.card-pill {
  padding: 6px 16px;
  border-radius: 999px;
  background: #fff0d9; /* 🔹 mais contraste */
  color: #cc6c00; /* 🔹 tom mais escuro para legibilidade */
  font-family: 'League Spartan', sans-serif;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  box-shadow: inset 0 0 3px rgba(255, 165, 0, 0.2);
}

/* ==== NÚMERO ==== */
.card-number {
  font-family: 'League Spartan', sans-serif;
  font-size: 34px;
  font-weight: 700;
  color: #ff8c00;
  margin-bottom: 6px;
}

/* ==== TEXTO INFERIOR ==== */
.card-footer {
  font-family: 'League Spartan', sans-serif;
  font-size: 13px;
  color: #777;
  margin: 0;
}
</style>