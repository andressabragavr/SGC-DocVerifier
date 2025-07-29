import json
import os

def salvar_resultado_em_json(conteudo_json_str: str, nome_arquivo: str, pasta_saida: str = None):
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

    if not pasta_saida:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        pasta_saida = os.path.join(root_dir, "data", "output")

    os.makedirs(pasta_saida, exist_ok=True)
    caminho_saida = os.path.join(pasta_saida, f"{nome_arquivo}.json")
    
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return caminho_saida
