<script lang="ts">
import Banner from './Banner.vue';
import alunoService from '../services/alunoService';
import { defineComponent } from 'vue';

export default defineComponent({
  components: { Banner },
  data() {
    return {
      dadosAluno: {
        nomeAluno: '',
        numCertificados: 0,
        horasLancadas: 0,
        horasFaltantes: 0,
        horasExigidas: 200
      }
    }
  },
  async mounted() {
    try {
      const usuario = localStorage.getItem('usuario');
      if (usuario) {
        const userObj = JSON.parse(usuario);
        this.dadosAluno.nomeAluno = userObj.name;

        // Busca os certificados do aluno via RA
        const response = await alunoService.getCertificadosPorRa(userObj.ra);
        const certificados = response.data;

        // Número total de certificados (independente do status)
        this.dadosAluno.numCertificados = certificados.length;

        // Filtra apenas os certificados com status "aprovado"
        const certificadosAprovados = certificados.filter(
          (cert: any) => cert.status === 'Aprovado'
        );

        // Soma das horas apenas dos certificados aprovados
        const totalHoras = certificadosAprovados.reduce(
          (acc: number, cert: any) => acc + cert.horasAtribuidas,
          0
        );
        this.dadosAluno.horasLancadas = totalHoras;

        // Cálculo de faltantes
        this.dadosAluno.horasFaltantes = Math.max(
          0,
          this.dadosAluno.horasExigidas - totalHoras
        );
      }
    } catch (error) {
      console.error('Erro ao carregar dados do aluno:', error);
    }
  }
});
</script>

<template>
    <Banner />
        <h3 class="welcome">Bem-vindo(a) {{ dadosAluno.nomeAluno }}!</h3>
        <div class="container-graph">
        <div class="itemsContainer">
            <div>
                <h2 class="titles">Certificados Cadastrados</h2>
                <h1 class="hours">{{ dadosAluno.numCertificados }}</h1>
            </div>
            <div>
                <h2 class="titles">Horas Lançadas</h2>
                <h1 class="hours">{{ dadosAluno.horasLancadas }}</h1>
            </div>
            <div>
                <h2 class="titles">Horas Faltantes</h2>
                <h1 class="hours">{{ dadosAluno.horasFaltantes }}</h1>
            </div>
            <div>
                <h2 class="titles">Horas Exigidas</h2>
                <h1 class="hours">{{ dadosAluno.horasExigidas }}</h1>
            </div>
        </div>
    <!-- <img src="../assets/grafico_pizza.jpeg" class="graph" /> -->
</div>
</template>

<style scoped>
* {
    font-family: 'League Spartan', sans-serif;
}

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
    align-items: center;
    width: 80%;
}

.titles {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
    margin-top: 15px;
}

.hours {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
    margin-top: 20px;
}

.container-graph {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: space-around;
    margin-top: 50px;
}

.graph {
    margin-top: 80px;
    margin-left: 150px;
}
</style>