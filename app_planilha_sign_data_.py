import os, hashlib, sys, io
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def limpar_dados(b):
    try:
        texto = b.decode('utf-8')
    except UnicodeDecodeError:
        texto = b.decode('cp1252') # Fallback para codificação padrão Windows Brasil
    texto = texto.replace('\r', '')
    return "\n".join([l.strip() for l in texto.splitlines() if l.strip()]).encode('utf-8')

def assinar():
    # Força o terminal a aceitar UTF-8 para evitar erros de emoji/acentos no Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Define caminhos absolutos baseados na localização deste script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_priv = os.path.join(base_dir, "..", "app_planilha_key_priv")
    caminho_dados = os.path.join(base_dir, "dados_planilha.csv")
    caminho_sig = os.path.join(base_dir, "app_planilha_signature.sig")

    try:
        with open(caminho_priv, "rb") as f:
            raw_key = f.read()
            private_key = serialization.load_pem_private_key(raw_key, password=None)
            key_id = hashlib.md5(raw_key).hexdigest()[:8]

        with open(caminho_dados, "rb") as f:
            dados = limpar_dados(f.read())

        assinatura = private_key.sign(
            dados,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        with open(caminho_sig, "wb") as f:
            f.write(assinatura)
        
        print(f"✅ Assinado! (ID da Chave Privada: {key_id})")

    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__": assinar()