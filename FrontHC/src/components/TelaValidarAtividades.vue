<script lang="ts">
import { defineComponent } from 'vue';
import coordenadorService from '../services/coordenadorService';
import BannerCoordenador from './BannerCoordenador.vue';

export default defineComponent({
  components: { BannerCoordenador },
  data() {
    return {
      dropdownItems: [] as any[]
    };
  },
  async mounted() {
    try {
      const alunos = await coordenadorService.getAlunosComCertificados();

      // Filtra apenas os certificados pendentes
      this.dropdownItems = alunos.flatMap((aluno: any) => {
        return aluno.certificados
          .filter((cert: any) => cert.status === 'Pendente')
          .map((cert: any) => ({
            id: cert.id,
            title: `${aluno.name} - ${aluno.ra} - ${aluno.curso}`,
            content: [
              `Tipo de Atividade: ${cert.tipoAtividade}`,
              `Título: ${cert.titulo}`,
              `Quantidade de Horas: ${cert.horasAtribuidas} horas`,
              `Data de Conclusão: ${new Date(cert.dataConclusao).toLocaleDateString('pt-BR')}`
            ],
            isOpen: false
          }));
      });
    } catch (error) {
      console.error('Erro ao buscar certificados:', error);
    }
  },
  methods: {
    toggleDropdown(index: number) {
      this.dropdownItems[index].isOpen = !this.dropdownItems[index].isOpen;
    },
    async acceptItem(index: number) {
      const certId = this.dropdownItems[index].id;
      await coordenadorService.aprovarCertificado(certId);
      this.dropdownItems.splice(index, 1); // remove da tela
    },
    async rejectItem(index: number) {
      const certId = this.dropdownItems[index].id;
      await coordenadorService.rejeitarCertificado(certId);
      this.dropdownItems.splice(index, 1); // remove da tela
    }
  }
});
</script>

<template>
    <BannerCoordenador />
    <h3 class="welcome">Bem-vindo Coordenador!</h3>
    <div class="container">
        <div class="dropdown-list">
            <div v-for="(item, index) in dropdownItems" 
                 :key="index" 
                 class="dropdown-item">
                <div class="dropdown-header" 
                     @click="toggleDropdown(index)">
                    {{ item.title }}
                    <span class="arrow" :class="{ 'open': item.isOpen }">▼</span>
                </div>
                <div class="dropdown-content" v-if="item.isOpen">
                    <ul>
                        <li v-for="(line, i) in item.content" :key="i">
                            {{ line }}
                        </li>
                    </ul>
                    <div class="button-container">
                        <button class="btn accept" @click="acceptItem(index)" title="Aceitar">
                            <span class="material-icons">check</span>
                        </button>
                        <button class="btn reject" @click="rejectItem(index)" title="Rejeitar">
                            <span class="material-icons">close</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.welcome {
    text-align: left;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    margin-left: 4rem;
    padding-bottom: 30px;
}

.container {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    align-items: center;
}

.dropdown-list {
    width: 100%;
}

.dropdown-item {
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.dropdown-header {
    padding: 15px;
    background-color: #f5f5f5;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'League Spartan', sans-serif;
}

.dropdown-header:hover {
    background-color: #e9e9e9;
}

.dropdown-content {
    padding: 15px;
    margin-left: 15px;
    background-color: white;
    font-family: 'League Spartan', sans-serif;
}

.arrow {
    transition: transform 0.3s ease;
}

.arrow.open {
    transform: rotate(180deg);
}

.button-container {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    /* margin-top: 5px; */
}

.btn {
    width: 30px;
    height: 30px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.accept {
    background-color: #4CAF50;
    color: white;
}

.accept:hover {
    background-color: #45a049;
    transform: scale(1.1);
}

.reject {
    background-color: #f44336;
    color: white;
}

.reject:hover {
    background-color: #da190b;
    transform: scale(1.1);
}

.material-icons {
    font-size: 24px;
}
</style>