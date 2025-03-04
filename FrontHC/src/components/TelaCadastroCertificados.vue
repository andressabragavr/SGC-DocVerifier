<script lang="ts">
import Banner from './Banner.vue';
import { defineComponent, ref } from 'vue';
import Tooltip from './Tooltip.vue';
  
export default defineComponent({
    name: 'TableWithTooltips',
    components: {Banner, Tooltip},

    data() {
      return {
        file: null as File | null,
        fileName: '',
      };
    },
    methods: {
      handleFileUpload(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
          this.file = target.files[0];
          this.fileName = this.file.name;
        }
      },
      triggerFileUpload() {
        (this.$refs.fileInput as HTMLInputElement).click();
      },
      submitForm() {
        if (this.file) {
          // Lógica para enviar o arquivo para o servidor
          console.log('Arquivo selecionado:', this.file);
        } 
        else {
          alert('Por favor, selecione um arquivo antes de enviar.');
        }
      },
    },
});
</script>

<template>
    <Banner />
    <h1 class="title">Cadastro de Certificados</h1>
    <div class="upload-container">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="certificate">
            <button type="button" class="upload-button" @click="triggerFileUpload">Selecionar arquivo PDF</button>
          </label>
          <input type="file" id="certificate" @change="handleFileUpload" accept=".pdf" required ref="fileInput" />
        </div>
        <div v-if="fileName" class="file-info">
          <p class="file-name">Arquivo selecionado: {{ fileName }}</p>
        </div>
        <button type="submit" class="submit-button">Upload</button>
      </form>
    </div>
    <h2 class="title">Tabela de Atividades</h2>
    <p class="Obs">Obs: das 200 horas necessárias para se graduar, 120 devem ser da categoria "Obrigatória" e 80 da categoria "Livre"</p>
    <div class="container-categorias">
      <table>
        <tr>
          <th>Categoria</th>
          <th>Tipos de Atividade</th>
          <th>Quantidade</th>
          <th>Horas Atribuídas</th>
          <th>Documentos Comprobatórios</th>
          <th>Realização do Envio</th>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Eventos Promovidos pela Facens</template>
              <template v-slot:tooltip>
                Participação no papel de apresentador e/ou expositor e/ou debatedor e/ou
                mediador e/ou organizador em congressos, seminários, simpósios, palestras,
                jornadas estudantis, mesa-redonda, visitas técnicas e oficinas, promovidas e/ou
                apoiadas pela Instituição.
            </template>
            </Tooltip>
          </td>
          <td>10</td>
          <td>4</td>
          <td>Lista nominal enviada à secretaria.</td>
          <td>Comissão Organizadora do Evento</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Atuação em Núcleos e Laboratórios da Facens</template>
              <template v-slot:tooltip>
                Participação voluntária e como membro ativo nos núcleos ou Laboratórios do
                curso prestando atendimento à comunidade Interna ou Externa, em horário extraclasse.
              </template>
            </Tooltip>
          </td>
          <td>6</td>
          <td>20</td>
          <td>Lista nominal enviada à secretaria.</td>
          <td>Coordenador de Curso</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Autor/Co-autor de Artigo de Cunho Científico</template>
              <template v-slot:tooltip>
                Participação como autor e/ou coautor de artigo publicado de cunho científico
                em revistas ou anais de congressos na área do curso frequentado.
              </template>
            </Tooltip>
          </td>
          <td>3</td>
          <td>40</td>
          <td>Cópia do artigo com ISBN ou ISSN e/ou cópia da declaração de aceite do congresso ou revista.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>CPA</template>
              <template v-slot:tooltip>
                Participação comprovada na avaliação institucional promovido pela CPA Comissão Permanente de Avaliação.
              </template>
            </Tooltip>
          </td>
          <td>4</td>
          <td>20</td>
          <td>Lista nominal enviada à secretaria.</td>
          <td>Presidente da CPA</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Cursos de Formação Complementar (oferecidos pela FACENS)</template>
              <template v-slot:tooltip>
                Participação como estudante em cursos de formação complementar oferecidos
                pela Facens na modalidade presencial ou EAD.
              </template>
            </Tooltip>
          </td>
          <td>10</td>
          <td>20</td>
          <td>Lista Nominal enviada à secretaria.</td>
          <td>Coordenador de Curso</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Iniciação Científica com Bolsa</template>
              <template v-slot:tooltip>
                Participação no papel de estudante-pesquisador bolsista em projetos de Iniciação Científica 
                ou Tecnológica com duração mínima de 200 horas, orientado ou co-orientado por docente da Facens.
              </template>
            </Tooltip>
          </td>
          <td>3</td>
          <td>60</td>
          <td>Relatório da atividade convalidado pelo coordenador do curso e/ou membros do NDE e/ou professor orientador.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Iniciação Científica sem Bolsa</template>
              <template v-slot:tooltip>
                Participação no papel de estudante-pesquisador voluntário de projetos de Iniciação Científica 
                ou Tecnológica com duração mínima de 200 horas e orientado ou co-orientado por docente da Facens.
              </template>
            </Tooltip>
          </td>
          <td>2</td>
          <td>60</td>
          <td>Relatório da atividade convalidado pelo coordenador do curso e/ou membros do NDE e/ou professor orientador.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Monitor na Facens</template>
              <template v-slot:tooltip>
                Participação como estudante em cursos de formação complementar oferecidos
                pela Facens na modalidade presencial ou EAD.
              </template>
            </Tooltip>
          </td>
          <td>3</td>
          <td>40</td>
          <td>Lista Nominal enviada à secretaria.</td>
          <td>Coordenador de Curso</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Monitor ou Instrutor de Cursos Abertos à Comunidade</template>
              <template v-slot:tooltip>
                Participação no papel de monitor e/ou instrutor e/ou produtor e/ou divulgador de forma voluntária 
                ou remunerada de eventos e/ou cursos e/ou treinamentos, abertos à comunidade ou não, com carga horária mínima de 16 horas.
              </template>
            </Tooltip>
          </td>
          <td>3</td>
          <td>40</td>
          <td>Cópia de declaração em papel timbrado da Instituição onde o curso foi ministrado e assinado pela coordenação e/ou membros do NDE.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Obrigatória</td>
          <td>
            <Tooltip>
              <template v-slot:default>Organização e Produção de Atividades Técnicas, Desportivas, Culturais e***</template>
              <template v-slot:tooltip>
                Ter papel ativo na produção, organização e participação em atividades desportivas, artísticas ou culturais (torneios interclasses, peças teatrais,
                recitais, sarau, cinema, apresentação musicais, dança) promovidas e/ou apoiada pela Direção/Coordenação do curso em que frequenta.
              </template>
            </Tooltip>
          </td>
          <td>5</td>
          <td>10</td>
          <td>Relatório da atividade convalidado pelo coordenador do curso e/ou membros do NDE e/ou professor organizador do evento.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Atividade Profissional ou Orientações Práticas em Laboratórios da IES</template>
              <template v-slot:tooltip>
                Atividades de caráter prático e profissionalizante desenvolvidos na FACENS
                sob a supervisão de Professores, na área de formação em horário extraclasse.
            </template>
            </Tooltip>
          </td>
          <td>2</td>
          <td>20</td>
          <td>Listagem com a relação de estudantes participantes.</td>
          <td>Coordenador de Curso</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Autor/Co-autor de Artigo de Cunho Tecnológico Não-científico</template>
              <template v-slot:tooltip>
                Participação como autor e/ou coautor de artigo publicado de cunho tecnológico/não-científico em revistas, 
                anais, blogs e sites conhecidos, de notória relevância e com boa qualidade de conteúdos na área de tecnologia.
              </template>
            </Tooltip>
          </td>
          <td>6</td>
          <td>10</td>
          <td>Cópia do artigo, cópia da capa ou documento comprobatório assinado pelo docente orientador, coordenador do curso ou membro do NDE.</td>
          <td>Aluno</td>
        </tr>
        <tr>
        <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Curso de Idioma</template>
              <template v-slot:tooltip>
                Cursos de idiomas com carga horária mínima de 60 horas semestrais e aproveitamento
                satisfatório. Não se aplica aos cursos de contenham disciplinas de idiomas na
                matriz curricular (Inglês/Espanhol) os demais idiomas poderão ser utilizados.
              </template>
            </Tooltip>
          </td>
          <td>4</td>
          <td>20</td>
          <td>Cópia do certificado de conclusão, constando carga horária mínima de 60 horas e aproveitamento satisfatório.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Cursos de Formação Complementar (fora da IES)</template>
              <template v-slot:tooltip>
                Participação como estudante/estudante em cursos de formação complementar
                (extensão) realizados fora da Facens na modalidade presencial ou EaD.
              </template>
            </Tooltip>
          </td>
          <td>8</td>
          <td>20</td>
          <td>Cópia do certificado de participação e a descrição da área, objetivos e carga horária.
              <br>(A carga horária será computada de acordo com a carga horária da atividade realizada).</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Disciplinas de Outros Cursos</template>
              <template v-slot:tooltip>
                Disciplinas cursadas com aproveitamento satisfatório em outros cursos ou IES que não tenham sido 
                compatibilizadas para aproveitamento de estudos no curso frequentado ou utilizadas na categoria de disciplinas eletivas.
              </template>
            </Tooltip>
          </td>
          <td>5</td>
          <td>20</td>
          <td>Cópia do Histórico Escolar.</td>
          <td>Secretaria</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Startups (Implementação de Plano de Negócio)</template>
              <template v-slot:tooltip>
                Participação comprovada na elaboração de um plano de negócios apresentados e contemplados com
                financiamento de investidor, patrocinador e/ou outros tipos de financiamentos não previstos.
              </template>
            </Tooltip>
          </td>
          <td>1</td>
          <td>100</td>
          <td>Cópia do Plano de Negócios e cópia de contratos estabelecidos.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Intercâmbio</template>
              <template v-slot:tooltip>
                Participação em intercâmbio com instituições parceiras, no âmbito nacional ou internacional.
              </template>
            </Tooltip>
          </td>
          <td>2</td>
          <td>40</td>
          <td>Cópia do comprovante de participação com assinatura do representante legal da instituição parceira ou cópia do contrato.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <Tooltip>
              <template v-slot:default>Ouvinte de Apresentação Pública de Dissertação ou Tese</template>
              <template v-slot:tooltip>
                Participação em seções públicas de defesa de dissertação (mestrado) e teses (doutorados) em assuntos aderentes ao projeto de 
                pesquisa científica e/ou tecnológica que participa ou que tenha aderência ao curso de graduação frequentado.
              </template>
            </Tooltip>
            <span style="cursor: pointer; text-decoration: underline;">
              Hover Over Me
              <v-tooltip activator="parent" location="bottom">Participação em seções públicas de defesa de dissertação (mestrado) e teses (doutorados) em assuntos aderentes ao projeto de 
                pesquisa científica e/ou tecnológica que participa ou que tenha aderência ao curso de graduação frequentado.</v-tooltip>
            </span>
          </td>
          <td>3</td>
          <td>10</td>
          <td>Cópia do certificado ou declaração de participação. Relatório convalidado pelo coordenador ou membros do NDE.</td>
          <td>Aluno</td>
        </tr>
        <tr>
          <td>Livre</td>
          <td>
            <!-- <Tooltip>
              <template v-slot:default>Participação em Atividade Competitiva (fora da FACENS) ***</template>
              <template v-slot:tooltip>
                Participação em intercâmbio com instituições parceiras, no âmbito nacional ou internacional.
              </template>
            </Tooltip> -->
            <v-tooltip text="Participação em intercâmbio com instituições parceiras, no âmbito nacional ou internacional.">
              <template v-slot:activator="{ props }">
                <span v-bind="props" style="cursor: pointer;">
                  Participação em Atividade Competitiva (fora da FACENS) ***
                </span>
              </template>
            </v-tooltip>
          </td>
          <td>4</td>
          <td>20</td>
          <td>Cópia do comprovante de participação com assinatura do representante legal da instituição parceira ou cópia do contrato.</td>
          <td>Aluno</td>
        </tr>
      </table>
    </div>
  </template>
  
<style scoped>
.title {
    text-align: center;
    font-family: 'League Spartan', sans-serif;
    margin-top: 4rem;
    padding-bottom: 30px;
}

.Obs {
  text-align: center;
  font-family: 'League Spartan', sans-serif;
}

.container-categorias {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 10px;
  border-radius: 60px;
  border: 50px solid #000;
  overflow: hidden;
  margin-bottom: 4rem;
}

th, td {
  border: 1px solid #000;
  padding: 8px;
  text-align: center;
  font-family: 'League Spartan', sans-serif;
  word-wrap: 
}

th {
  background-color: #FF8C00;
}

th:first-child { 
  border-top-left-radius: 10px; 
} 

th:last-child { 
  border-top-right-radius: 10px; 
} 

td:first-child { 
  border-bottom-left-radius: 10px; 
} 

td:last-child { 
  border-bottom-right-radius: 10px; 
}

.upload-container {
    max-width: 500px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    align-items: center;
}

.form-group {
    margin-bottom: 15px;
    text-align: center;
}
  
.upload-button {
    background-color: #FF8C00; /* Cor vermelha */
    color: white;
    padding: 15px 50px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 18px;
    font-family: 'League Spartan', sans-serif;
}
  
.upload-button:hover {
    background-color: #FF4500; /* Cor vermelha mais escura ao passar o mouse */
}
  
input[type="file"] {
    display: none;
}
  
.file-info {
    text-align: center;
    margin-top: 10px;
}

.file-name {
  font-family: 'League Spartan', sans-serif;
}
  
.submit-button {
    display: block;
    padding: 10px 80px;
    margin-left: 125px;
    margin-top: 30px;
    border: none;
    background-color: #A3A0A0;
    color: white;
    font-size: 17px;
    font-family: 'League Spartan', sans-serif;
    border-radius: 5px;
    cursor: pointer;
}
  
.submit-button:hover {
    background-color: #000;
}

@media only screen and (max-width: 1300px) {
  th, td {
    padding: 12px 5px;
    font-size: 14px;
  }
}

@media only screen and (max-width: 767px) {
  th, td {
    padding: 12px 5px;
    font-size: 14px;
  }
}
</style>  