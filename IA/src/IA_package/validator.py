import json

def validar_data(ra):
  # extração ano RA
  ra = str(ra)
  ano_RA = int(ra[:2])
  
  if ano_RA < 100:
    ano_entrada = ano_RA + 2000
  
  # extração ano no certificado
  with open("certificados.json", "r", encoding="utf-8") as f:
    certificados = json.load(f)
    
  if not certificados:
    return False
    
  for cert in certificados:
    data_emissao = cert.get("data_emissao")
    
    if not data_emissao:
      return False
    
    try:
      ano_certificado = int(data_emissao[:4])
    except (ValueError, TypeError):
      return False
    
    if ano_certificado < ano_entrada:
      return False
    
  return True and print("Data válida")