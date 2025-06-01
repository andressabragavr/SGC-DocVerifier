import magic

class DetectorTipoService:
    """
    Serviço responsável por detectar o tipo MIME de um arquivo enviado pelo usuário e classificá-lo como PDF, PNG ou JPEG.
    """
    
    SUPORTADOS = {
        "application/pdf": "pdf",
        "image/png": "png",
        "image/jpeg": "jpeg"
        # adicionar mais tipos conforme necessário
    }
    
    def detectar_tipo_arquivo(self, caminho_arquivo: str) -> str:
        """
        Detecta o tipo MIME de um arquivo.

        Args:
            caminho_arquivo (str): Caminho do arquivo a ser verificado.

        Raises:
            ValueError: Se o tipo MIME não for suportado.

        Returns:
            str: Tipo do arquivo detectado (pdf, png, jpeg).
        """
        tipo_mime = magic.from_file(caminho_arquivo, mime = True)
        
        if tipo_mime in self.SUPORTADOS:
            return self.SUPORTADOS[tipo_mime]
        
        raise ValueError(f"Tipo de arquivo não suportado: {tipo_mime}")