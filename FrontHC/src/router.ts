import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import TelaLogin from './components/TelaLogin.vue';
import TelaCadastro from './components/TelaCadastro.vue';
import TelaInicialAluno from './components/TelaInicialAluno.vue';
import TelaHistorico from './components/TelaHistorico.vue';
import TelaCadastroCertificados from './components/TelaCadastroCertificados.vue';
import TelaConsultarHistorico from './components/TelaConsultarHistorico.vue';
import TelaRelatorio from './components/TelaRelatorio.vue';
import TelaInicialCoordenador from './components/TelaInicialCoordenador.vue';


const routes: Array<RouteRecordRaw> = [
    { path: '/', name: 'TelaLogin', component: TelaLogin },
    { path: '/TelaCadastro', name: 'TelaCadastro', component: TelaCadastro },
    { path: '/TelaInicialAluno', name: 'TelaInicialAluno', component: TelaInicialAluno },
    { path: '/TelaCadastroCertificados', name: 'TelaCadastroCertificados', component: TelaCadastroCertificados },
    { path: '/TelaHistorico', name: 'TelaHistorico', component: TelaHistorico},
    { path: '/TelaConsultarHistorico', name: 'TelaConsultarHistorico', component: TelaConsultarHistorico },
    { path: '/TelaRelatorio', name: 'TelaRelatorio', component: TelaRelatorio },
    { path: '/TelaInicialCoordenador', name: 'TelaInicialCoordenador', component: TelaInicialCoordenador }
  ];

  const router = createRouter({
    history: createWebHistory(),
    routes
  });

  export default router;