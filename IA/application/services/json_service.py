import json
import os

def salvar_resultado_em_json(conteudo_json_str: str, nome_arquivo: str, pasta_saida: str = "data/output"):
    """
    Trata a string JSON retornada pela LLM e salva em um arquivo .json.
    """
    if conteudo_json_str.startswith("```json"):
        conteudo_json_str = conteudo_json_str[7:]
    if conteudo_json_str.endswith("```"):
        conteudo_json_str = conteudo_json_str[:-3]

    try:
        dados = json.loads(conteudo_json_str.strip())
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return None

    os.makedirs(pasta_saida, exist_ok=True)
    caminho_saida = os.path.join(pasta_saida, f"{nome_arquivo}.json")
    
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return caminho_saida
