import json
from langchain_ollama import ChatOllama

import warnings
warnings.filterwarnings("ignore")

def extrair_informacoes_certificados(texto_dict, num_cert, nome_aluno, atividades, contexto_adicional=""):
    """
    Constrói o prompt para extrair informações dos certificados e invoca o modelo.
    
    Parâmetros:
      - texto_dict: Dicionário contendo o texto extraído do certificado.
      - num_cert: Número de certificados presentes.
      - nome_aluno: Nome do aluno (ou parte dele) a ser extraído.
      - atividades: Valor padrão para a quantidade de horas, caso não haja número explícito.
    
    Retorna:
      - O resultado da invocação do modelo (espera-se que seja um JSON formatado).
    """
    prompt = f"""
    {contexto_adicional}
Você é um assistente que extrai informações de certificados. Responda apenas com o JSON solicitado, sem comentários ou código.

Você recebe o texto extraído de um certificado em um dicionário: {texto_dict} que contém {num_cert} certificado(s).

Seu objetivo é analisar esse dicionário e extrair as seguintes informações:

1. **Data de emissão**:
   - Procure menções de data em qualquer um dos formatos:
     - "DD de mês de AAAA" (ex.: "20 de outubro de 2023")
     - "DD/MM/AAAA" (ex.: "20/10/2023")
     - "AAAA-MM-DD" (ex.: "2023-10-20")
   - Se houver várias datas no texto, escolha aquela que esteja mais claramente associada à emissão do certificado 
     (por exemplo, precedida por expressões como "Data de emissão", "Certificamos em", ou próxima ao final do documento).
   - Sempre retorne a data no formato "YYYY-MM-DD".
   - Se não encontrar nenhuma data válida, retorne "N/A".
   - Não invente datas que não apareçam no texto.

2. **Nome do aluno**:
   - Você recebe um valor de referência "{nome_aluno}".
   - Procure no texto do certificado um nome que seja **exatamente igual ou o mais próximo possível** de "{nome_aluno}", ignorando:
     - Acentos
     - Maiúsculas/minúsculas
     - Pequenas variações de abreviação.
   - Se encontrar **exatamente um** nome que seja claramente uma variação de "{nome_aluno}", retorne o nome completo "{nome_aluno}".
   - Se o certificado contiver vários nomes e não ficar claro qual corresponde a "{nome_aluno}", ou se nenhum nome for suficientemente parecido, retorne "N/A".
   - **Evite retornar "N/A"** se identificar uma variação que corresponda a "{nome_aluno}".
 
3. **Tipo de certificado**:
   - O valor retornado deve ser exatamente um dos seguintes: Artigo Científico, Artigo Tecnológico, Curso de Formação, Evento Acadêmico, Participação em Núcleo, Atividade Profissional, Monitoria, Voluntariado, Intercâmbio, Iniciação Científica, Comissão Organizadora de Evento, Participação em Órgão de Representação Acadêmica, Participação em Eventos como Ouvinte, Cursos de Idiomas, Startup / Implementação de Plano de Negócio.
   - Se o certificado não se encaixar em nenhuma dessas categorias, retorne "N/A".

4. **Quantidade de horas**:
   - Procure por menções como:
     - "XX hora"
     - "XX horas"
     - "XXh"
     - "carga horária: XX"
     - "carga horária: XXh"
     - "carga horária: XX horas"
   - Se algum desses padrões for encontrado, extraia e RETORNE APENAS O NÚMERO IDENTIFICADO.
   - Caso nenhum número seja encontrado nesses padrões, então retorne, SEMPRE, o valor padrão de horas definido em {atividades} para o "tipo_certificado" identificado.
   - Se o "tipo_certificado" não corresponder a nenhuma das categorias em {atividades}, retorne "N/A".
     
Retorne **somente** o JSON no seguinte formato para TODOS OS {num_cert} CERTIFICADOS PRESENTES:

[
  {{
    "nome": "[Nome do aluno em formato padrão ou "N/A"]",
    "data_emissao": "[YYYY-MM-DD ou "N/A"]",
    "tipo_certificado": "[Nome da atividade correta ou "N/A"]",
    "quantidade_horas": "[Número de horas ou "N/A"]"
  }}
]
"""

    # Instancia o modelo. Certifique-se de que a classe ChatOllama está importada.
    # model = ChatOllama(model="llama3.3")
    model = ChatOllama(model="llama3.1")
    resultado_modelo = model.invoke(prompt)
    print("resultado_modelo: ",resultado_modelo)
    return resultado_modelo

def salvar_certificados(mensagem, caminho_saida: str):
    """
    Recebe um objeto AIMessage (ou uma string JSON) com os certificados,
    extrai o conteúdo e salva exatamente os dados retornados em um arquivo JSON.
    """
    # Se o objeto possui o atributo 'content', extraímos a string
    if hasattr(mensagem, 'content'):
        conteudo = mensagem.content
    else:
        conteudo = mensagem

    try:
        # Converte a string JSON para objeto Python
        dados = json.loads(conteudo)
        print("dados:", dados)
    except json.JSONDecodeError as e:
        print("Erro ao decodificar o JSON:", e)
        return

    # Salva o objeto sem nenhuma modificação
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)