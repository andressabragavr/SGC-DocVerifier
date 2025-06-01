def carregar_prompt_formatado(
    caminho: str,
    texto_dict: str,
    num_cert: int,
    nome_aluno: str,
    atividades: str,
    contexto: str
) -> str:
    """
    Lê o arquivo de prompt base e substitui os placeholders por seus respectivos valores.
    """
    with open(caminho, "r", encoding="utf-8") as f:
        template = f.read()
    
    return template.format(
        texto_dict = texto_dict,
        num_cert = num_cert,
        nome_aluno = nome_aluno,
        atividades = atividades,
        contexto = contexto
    )