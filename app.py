from flask import Flask, render_template, request
import csv
import os
import io

app = Flask(__name__)

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
VERSAO_APP = "1.1.0" 

MENU_SISTEMA = [
    {"nome": "Home", "url": "/appcomissao/", "icone": "🏠"},
    {
        "nome": "Dados", 
        "icone": "📂", 
        "sub_itens": [
            {"nome": "Ler Dados", "url": "/appcomissao/ler_dados", "icone": "📥"},
            {"nome": "Processar Comissões", "url": "/appcomissao/comissao", "icone": "⚙️"}
        ]
    },
    {"nome": "Comissões", "url": "/appcomissao/comissao", "icone": "💰"},
    {"nome": "Contato", "url": "/appcomissao/contato", "icone": "✉️"},
    {"nome": "Relatórios", "url": "/appcomissao/relatorios", "icone": "📈"}
]

# ==========================================
# 2. LÓGICA DE NEGÓCIO (OBJETO DE SERVIÇO)
# ==========================================
class ComissaoService:
    """Gerencia o processamento, cálculos e validação das comissões."""
    
    TAXA_COMISSAO = 0.10  # 10% de comissão sobre o total da venda
    
    @staticmethod
    def _calcular_valores_linha(linha):
        """Calcula totais e comissão para uma linha do CSV."""
        try:
            # 1. Extração dos valores brutos (Garante 0 se a coluna estiver vazia ou ausente)
            # Nota: Usamos os nomes exatos das colunas do arquivo dados_planilha.csv
            venda_total = (
                float(linha.get('VL_SETUP', 0)) + 
                float(linha.get('VL_TOTEM', 0)) + 
                float(linha.get('VL_LICENÇA', 0))
            )
            
            # 2. Cálculo da comissão (Venda Total * 10%)
            comissao = venda_total * ComissaoService.TAXA_COMISSAO
            
            return {
                "vendedor": linha.get('CLIENTE', 'Desconhecido'),
                "valor_venda": venda_total,
                "taxa": ComissaoService.TAXA_COMISSAO * 100,
                "valor_comissao": comissao
            }
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _executar_processamento(leitor_csv):
        """Lógica centralizada para iterar no CSV e somar totais."""
        itens = []
        total_vendas = 0.0
        total_comissoes = 0.0

        for linha in leitor_csv:
            resultado = ComissaoService._calcular_valores_linha(linha)
            if resultado:
                itens.append(resultado)
                total_vendas += resultado['valor_venda']
                total_comissoes += resultado['valor_comissao']

        return {
            "itens": itens,
            "total_vendas": total_vendas,
            "total_comissoes": total_comissoes,
            "total_linhas": len(itens)
        }

    @staticmethod
    def carregar_dados_padrao():
        """Lê o arquivo local dados_planilha.csv."""
        caminho_arquivo = os.path.join(os.path.dirname(__file__), "dados_planilha.csv")
        
        if not os.path.exists(caminho_arquivo):
            return {"erro": "Arquivo padrão não encontrado."}

        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            leitor = csv.DictReader(f)
            dados = ComissaoService._executar_processamento(leitor)
            dados['origem'] = "Arquivo Padrão (Local)"
            return dados

    @staticmethod
    def processar_arquivo_upload(arquivo):
        """Processa o arquivo enviado via formulário."""
        if not arquivo or arquivo.filename == '':
            return None
        
        # Transforma o stream do upload em um formato que o csv.DictReader entenda
        stream = io.StringIO(arquivo.stream.read().decode("UTF8"), newline=None)
        leitor = csv.DictReader(stream)
        
        dados = ComissaoService._executar_processamento(leitor)
        dados['origem'] = f"Upload: {arquivo.filename}"
        return dados

# ==========================================
# 2. ROTAS
# ==========================================

@app.route('/')
def home():
    return render_template('index.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

@app.route('/ler_dados')
def ler_dados():
    return render_template('ler_dados.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

@app.route('/comissao', methods=['GET', 'POST'])
def comissao():
    dados_processados = None
    if request.method == 'POST':
        modo_apresentacao = request.form.get('modo_apresentacao') == 'true'
        
        if modo_apresentacao:
            dados_processados = ComissaoService.carregar_dados_padrao()
        else:
            arquivo = request.files.get('arquivo_csv')
            dados_processados = ComissaoService.processar_arquivo_upload(arquivo)
            
    return render_template('comissao.html', menu=MENU_SISTEMA, versao=VERSAO_APP, dados=dados_processados)

@app.route('/contato')
def contato():
    return render_template('contato.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

# ==========================================
# 3. INICIAR O SERVIDOR
# ==========================================
if __name__ == '__main__':
    # Importamos o Dispatcher apenas para o teste local
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from flask import Flask

    # Criamos um app "vazio" para ser a raiz local
    app_raiz = Flask(__name__)

    # Montamos o seu app principal dentro de /appcomissao
    app.wsgi_app = DispatcherMiddleware(app_raiz.wsgi_app, {
        '/appcomissao': app.wsgi_app
    })

    # Agora o Flask vai responder em http://127.0.0.1:5000/appcomissao
    print("Servidor rodando em: http://127.0.0.1:5000/appcomissao")
    app.run(port=5000, debug=True)