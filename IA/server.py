from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI(
    title="DocVerifier API",
    description="API para processar certificados via main.py",
    version="1.0.0"
)

# Modelo de entrada esperado no JSON
class Entrada(BaseModel):
    caminho_arquivo: str
    nome_aluno: str

@app.post("/processar")
async def processar(dados: Entrada):
    """
    Executa o main.py como script, passando caminho_arquivo e nome_aluno
    """
    try:
        # Executa o main.py como subprocesso
        result = subprocess.run(
            ["python", "main.py", dados.caminho_arquivo, dados.nome_aluno],
            capture_output=True,
            text=True
        )

        # Se deu erro no script
        if result.returncode != 0:
            return {"erro": result.stderr.strip()}

        # Resposta normal (JSON do main.py já vem formatado como string)
        return {"resultado": result.stdout.strip()}

    except Exception as e:
        return {"erro": str(e)}
