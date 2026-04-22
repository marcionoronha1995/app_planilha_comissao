import json, hashlib, sys, io, os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def limpar_dados(b):
    try:
        texto = b.decode('utf-8')
    except UnicodeDecodeError:
        texto = b.decode('cp1252') # Fallback para codificação padrão Windows Brasil
    texto = texto.replace('\r', '')
    return "\n".join([l.strip() for l in texto.splitlines() if l.strip()]).encode('utf-8')

def verificar():
    # Força o terminal a aceitar UTF-8 para evitar erros de emoji/acentos no Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_pub = os.path.join(base_dir, "app_planilha_key_pub")
    caminho_dados = os.path.join(base_dir, "dados_planilha.csv")
    caminho_sig = os.path.join(base_dir, "app_planilha_signature.sig")
    caminho_manifest = os.path.join(base_dir, "app_planilha_manifest.json")

    try:
        with open(caminho_pub, "rb") as f:
            raw_key = f.read()
            public_key = serialization.load_pem_public_key(raw_key)
            # Gera o ID para comparar
            key_id = hashlib.md5(raw_key).hexdigest()[:8]

        with open(caminho_dados, "rb") as f:
            dados = limpar_dados(f.read())
        
        with open(caminho_sig, "rb") as f:
            assinatura = f.read()

        public_key.verify(
            assinatura, dados,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

        with open(caminho_manifest, "r", encoding="utf-8") as f:
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