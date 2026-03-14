import json, hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def limpar_dados(b):
    texto = b.decode('utf-8', errors='ignore').replace('\r', '')
    return "\n".join([l.strip() for l in texto.splitlines() if l.strip()]).encode('utf-8')

def verificar():
    try:
        with open("app_planilha_key_pub", "rb") as f:
            raw_key = f.read()
            public_key = serialization.load_pem_public_key(raw_key)
            # Gera o ID para comparar
            key_id = hashlib.md5(raw_key).hexdigest()[:8]

        with open("dados_planilha.csv", "rb") as f:
            dados = limpar_dados(f.read())
        
        with open("app_planilha_signature.sig", "rb") as f:
            assinatura = f.read()

        public_key.verify(
            assinatura, dados,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        with open("app_planilha_manifest.json", "r", encoding="utf-8") as f:
            m = json.load(f)
            
        print("-" * 45)
        print(f"✅ SUCESSO! (ID da Chave Pública: {key_id})")
        print(f"Autor: {m['autor']} | Local: {m['local']}")
        print("-" * 45)

    except Exception:
        # Tenta pegar o ID mesmo em caso de erro para diagnóstico
        with open("app_planilha_key_pub", "rb") as f:
            err_id = hashlib.md5(f.read()).hexdigest()[:8]
        print(f"❌ FALHA! (ID da Chave Pública: {err_id})")
        print("Os IDs combinam? Se não, apague a chave na pasta anterior e gere de novo.")

if __name__ == "__main__": verificar()