import subprocess
import sys
import os
import time
import io

# 1. Ajuste de Encoding (Mantendo sua estrutura original)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- CONFIGURAÇÃO DE CAMINHOS ---
VENV_PYTHON = r"E:\Github\MeusProjetos\.venv\Scripts\python.exe"
BASE_DIR = r"E:\Github\MeusProjetos\app_planilha_comissao"
APP_PY = os.path.join(BASE_DIR, "app.py")

def limpar_arquivos_sistema():
    """Remove desktop.ini do projeto e da biblioteca problemática na venv."""
    print("[*] Realizando limpeza profunda (Removendo desktop.ini)...")
    
    # Caminho da biblioteca que está dando erro
    caminho_biblioteca = r"e:\Github\MeusProjetos\.venv\Lib\site-packages\jsonschema_specifications\schemas"
    
    # Limpa na pasta do projeto e na pasta da biblioteca específica
    pastas_para_limpar = [BASE_DIR, caminho_biblioteca]
    
    for pasta in pastas_para_limpar:
        if os.path.exists(pasta):
            ps_cmd = f'Get-ChildItem -Path "{pasta}" -Filter "desktop.ini" -Recurse -Force | Remove-Item -Force'
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    
    print("    ✅ Ambiente desobstruído.")

def encerrar_servidores_antigos():
    print("[*] Verificando portas 5000 e 8888...")
    # Agora encerra também a porta 8888 usada pelo Jupyter/Colab
    for porta in [5000, 8888]:
        ps_cmd = f'Stop-Process -Id (Get-NetTCPConnection -LocalPort {porta} -ErrorAction SilentlyContinue).OwningProcess -Force'
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    print("    ✅ Portas liberadas.")

def executar_script(nome_arquivo, descricao):
    caminho_script = os.path.join(BASE_DIR, nome_arquivo)
    print(f"[*] {descricao}...")
    proc = subprocess.run([VENV_PYTHON, caminho_script], capture_output=True)
    
    if proc.returncode == 0:
        print(f"    ✅ {descricao}: OK.")
        return True
    else:
        try:
            erro = proc.stderr.decode('cp1252', errors='replace')
        except:
            erro = str(proc.stderr)
        print(f"    ❌ ERRO em {descricao}: {erro}")
        return False

def iniciar_servidor_python_powershell():
    """Inicia o servidor Flask em nova janela."""
    print(f"\n[🌐] Disparando Servidor Flask em janela externa...")
    comando_interno = f"Set-Location '{BASE_DIR}'; & '{VENV_PYTHON}' '{APP_PY}'"
    os.system(f'start powershell -NoExit -Command "{comando_interno}"')

# --- NOVA FUNÇÃO PARA O COLAB ---
def iniciar_servidor_colab_powershell():
    """Inicia o servidor Jupyter para conexão do Google Colab em nova janela."""
    print(f"[📡] Disparando Servidor para Colab (Porta 8888)...")
    
    # Parâmetros necessários para o Colab aceitar a conexão local
    comando_colab = (
        f"Set-Location '{BASE_DIR}'; & '{VENV_PYTHON}' -m jupyter server "
        f"--ServerApp.allow_origin='https://colab.research.google.com' "
        f"--port=8888 --ServerApp.port_retries=0 --ServerApp.token='' "
        f"--ServerApp.password='' --ServerApp.disable_check_xsrf=True --no-browser"
    )
    
    os.system(f'start powershell -NoExit -Command "{comando_colab}"')

def main():
    print("=" * 60)
    print("💎 SISTEMA DE COMISSÃO - FLASK + COLAB")
    print("=" * 60)

    os.chdir(BASE_DIR)

    # 1. Preparação
    limpar_arquivos_sistema()
    encerrar_servidores_antigos()

    # 2. Auditoria
    if executar_script("verificar_consistencia.py", "Auditoria de Dados"):
        
        # 3. Inicialização dos Servidores
        iniciar_servidor_colab_powershell() # Servidor Colab (8888)
        time.sleep(2)
        iniciar_servidor_python_powershell() # Servidor Flask (5000)
        
        print("\n" + "=" * 60)
        print("✅ SERVIDORES INICIADOS")
        print("Use a porta 5000 para o site e 8888 para o Colab.")
        print("=" * 60)
    else:
        print("\n❌ ABORTADO: Falha na auditoria.")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()