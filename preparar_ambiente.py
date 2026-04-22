import subprocess
import sys
import os
import io

# Ajuste de Encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# CONFIGURAÇÃO DE CAMINHOS
VENV_PYTHON = r"E:\Github\MeusProjetos\.venv\Scripts\python.exe"
BASE_DIR = r"E:\Github\MeusProjetos\app_planilha_comissao"

def limpar_arquivos_sistema():
    print("[*] Limpando arquivos residuais (desktop.ini)...")
    ps_cmd = f'Get-ChildItem -Path "{BASE_DIR}" -Filter "desktop.ini" -Recurse -Force | Remove-Item -Force'
    subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    print("    ✅ Ambiente limpo.")

def encerrar_servidores_antigos():
    print("[*] Verificando portas 5000 e 8888...")
    for porta in [5000, 8888]:
        ps_cmd = f'Stop-Process -Id (Get-NetTCPConnection -LocalPort {porta} -ErrorAction SilentlyContinue).OwningProcess -Force'
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    print("    ✅ Conflitos de rede resolvidos.")

def executar_auditoria(nome_arquivo):
    caminho_script = os.path.join(BASE_DIR, nome_arquivo)
    print(f"[*] Executando Auditoria de Dados...")
    proc = subprocess.run([VENV_PYTHON, caminho_script], capture_output=True)
    
    if proc.returncode == 0:
        print("    ✅ Dados consistentes.")
        return True
    else:
        print(f"    ❌ FALHA NA AUDITORIA: {proc.stderr.decode('cp1252', errors='replace')}")
        return False

def main():
    print("=" * 50)
    print("🛠️  PREPARAÇÃO DO SISTEMA DE COMISSÃO")
    print("=" * 50)
    
    os.chdir(BASE_DIR)
    limpar_arquivos_sistema()
    encerrar_servidores_antigos()
    
    if executar_auditoria("verificar_consistencia.py"):
        print("\n[PRONTO] O ambiente está ok. Inicie os servidores manualmente.")
    else:
        print("\n[ERRO] Resolva os problemas de dados antes de iniciar.")

if __name__ == "__main__":
    main()