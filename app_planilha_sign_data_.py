import os, hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def limpar_dados(b):
    texto = b.decode('utf-8', errors='ignore').replace('\r', '')
    return "\n".join([l.strip() for l in texto.splitlines() if l.strip()]).encode('utf-8')

def assinar():
    try:
        with open("../app_planilha_key_priv", "rb") as f:
            raw_key = f.read()
            private_key = serialization.load_pem_private_key(raw_key, password=None)
            # Gera um ID da chave para conferência
            key_id = hashlib.md5(raw_key).hexdigest()[:8]

        with open("dados_planilha.csv", "rb") as f:
            dados = limpar_dados(f.read())

        assinatura = private_key.sign(
            dados,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        with open("app_planilha_signature.sig", "wb") as f:
            f.write(assinatura)
        
        print(f"✅ Assinado! (ID da Chave Privada: {key_id})")

    except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__": assinar()