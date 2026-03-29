from flask import Flask, render_template

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
    app.run(debug=True)