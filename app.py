from flask import Flask, render_template, request

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
    """Objeto responsável por gerenciar o processamento de dados."""
    
    @staticmethod
    def carregar_dados_padrao():
        # Aqui você colocará a lógica para ler o CSV padrão
        # Por enquanto, retorna uma simulação
        return {"status": "sucesso", "origem": "padrão"}

    @staticmethod
    def processar_arquivo_upload(arquivo):
        # Lógica para processar o arquivo enviado pelo usuário
        return {"status": "sucesso", "origem": "upload"}

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
    if request.method == 'POST':
        modo_apresentacao = request.form.get('modo_apresentacao') == 'true'
        
        if modo_apresentacao:
            dados = ComissaoService.carregar_dados_padrao()
        else:
            arquivo = request.files.get('arquivo_csv')
            dados = ComissaoService.processar_arquivo_upload(arquivo)
            
    return render_template('comissao.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

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