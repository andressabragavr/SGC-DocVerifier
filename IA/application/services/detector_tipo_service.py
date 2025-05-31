import magic

class DetectorTipoService:
    
    SUPORTADOS = {
        "application/pdf": "pdf",
        "image/png": "png",
        "image/jpeg": "jpeg"
        # adicionar mais tipos conforme necessário
    }
    
    def detectar_tipo_arquivo(self, caminho_arquivo: str) -> str:
        tipo_mime = magic.from_file(caminho_arquivo, mime = True)
        
        if tipo_mime in self.SUPORTADOS:
            return self.SUPORTADOS[tipo_mime]
        
        raise ValueError(f"Tipo de arquivo não suportado: {tipo_mime}")