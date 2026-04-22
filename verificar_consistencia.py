import csv
import os
import sys
import io

def verificar_consistencia(caminho_arquivo):
    # Força o terminal a aceitar UTF-8 para evitar erros de emoji no Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(f"🔍 Iniciando auditoria de dados: {caminho_arquivo}")
    erros = []
    
    # Regras de Negócio (Valores Unitários)
    SETUP_UNIT = 250.0
    TOTEM_UNIT = 2250.0
    LICENCA_UNIT = 75.0

    if not os.path.exists(caminho_arquivo):
        print("❌ Erro: Arquivo de dados não encontrado.")
        return

    with open(caminho_arquivo, mode='r', encoding='utf-8-sig', errors='replace') as f:
        leitor = csv.DictReader(f)
        for i, linha in enumerate(leitor, start=2):
            try:
                pdv = int(linha['QDT_PDV'])
                setup = float(linha['VL_SETUP'])
                totem = float(linha['VL_TOTEM'])
                licenca = float(linha['VL_LICENÇA'])
                status = linha['STATUS_FINANCEIRO']
                dt_ini = linha['DATA_PRIMEIRO_PG']
                dt_fim = linha['DATA_ULTIMO_PG']

                # Validação de Cálculos Proporcionais
                if setup != pdv * SETUP_UNIT:
                    erros.append(f"Linha {i} ({linha['CLIENTE']}): VL_SETUP ({setup}) não confere com QDT_PDV ({pdv}). Esperado: {pdv * SETUP_UNIT}")
                
                if totem != pdv * TOTEM_UNIT:
                    erros.append(f"Linha {i} ({linha['CLIENTE']}): VL_TOTEM ({totem}) não confere com QDT_PDV ({pdv}). Esperado: {pdv * TOTEM_UNIT}")

                if licenca != pdv * LICENCA_UNIT:
                    erros.append(f"Linha {i} ({linha['CLIENTE']}): VL_LICENÇA ({licenca}) não confere com QDT_PDV ({pdv}). Esperado: {pdv * LICENCA_UNIT}")

                # Validação de Lógica de Datas vs Status
                if status == 'PENDENTE' and (dt_ini or dt_fim):
                    erros.append(f"Linha {i}: Status PENDENTE mas contém datas de pagamento.")
                
                if status == 'PAGO' and (not dt_ini or not dt_fim):
                    erros.append(f"Linha {i}: Status PAGO mas faltam datas de primeiro ou último pagamento.")

            except ValueError as e:
                erros.append(f"Linha {i}: Erro de formatação numérica ou de data.")

    if not erros:
        print("✅ SUCESSO: Todos os 208 registros estão consistentes.")
    else:
        print(f"❌ FALHA: Encontrados {len(erros)} erros de consistência:")
        for erro in erros:
            print(f"   - {erro}")

if __name__ == "__main__":
    verificar_consistencia("dados_planilha.csv")