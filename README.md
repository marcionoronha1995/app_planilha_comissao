# 📊 Sistema de Gestão e Segurança - App Planilha Comissão

# app_planilha_comissao
Este programa funciona como uma planilha inteligente: ele recebe valores de vendas, calcula automaticamente a comissão devida e gera um novo arquivo de planilha processado com todos os dados calculados.

Todo o processo é protegido por criptografia RSA para garantir que os cálculos e os dados dos clientes não sejam violados.

## 🛠️ O que cada aplicação faz?

| Arquivo | Função |
| :--- | :--- |
| **`app_planilha_write_key_.py`** | **Gerador de Identidade**: Cria o par de chaves (Pública/Privada) e o manifesto. Define quem é o autor do sistema. |
| **`app_planilha_sign_data_.py`** | **Carimbo Digital**: Assina os dados brutos. É o que garante que a comissão calculada é legítima. |
| **`app_planilha_desbloquear.py`** | **Validador**: Verifica se a planilha de comissões foi alterada indevidamente. |
| **`dados_planilha.csv`** | **Banco de Dados**: Contém os valores de entrada (vendas, CNPJ, clientes). |
| **`processar_comissao.py`** | **Motor de Cálculo**: Lê os dados, aplica as regras de comissão e gera o arquivo de saída. |

---

## 🚀 Fluxo de Trabalho (Passo a Passo para Commit)

Toda vez que você for atualizar o sistema ou os dados e enviar para o GitHub, siga esta ordem para manter a segurança:

1.  **Atualizar Dados**: Insira as novas vendas ou clientes no `dados_planilha.csv`.
2.  **Processar (Se aplicável)**: Rode o script de cálculo para gerar os resultados de comissão.
3.  **Assinar a Versão (CRÍTICO)**:
    ```bash
    python app_planilha_sign_data_.py
    ```
    *Isso gera um novo arquivo `.sig` que "trava" os dados atuais com sua assinatura.*
4.  **Testar Verificação**:
    ```bash
    python app_planilha_desbloquear.py
    ```
    *Garanta que apareça a mensagem de **SUCESSO**.*
5.  **Enviar para o GitHub**:
    ```bash
    git add .
    git commit -m "feat: atualização de dados e recálculo de comissões"
    git push origin main
    ```

---

## 🔐 Segurança das Chaves
* **Chave Privada**: Fica em `../app_planilha_key_priv` (fora do GitHub).
* **Chave Pública**: Fica no repositório para permitir a conferência dos dados por qualquer interessado.

---

## 📝 Requisitos
* Python 3.x
* Biblioteca `cryptography` (`pip install cryptography`)