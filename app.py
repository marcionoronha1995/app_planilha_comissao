from flask import Flask, render_template

app = Flask(__name__)

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
# A sua lista de configuração do menu (no topo, para todas as rotas enxergarem)
MENU_SISTEMA = [
    {"nome": "Home", "url": "/", "icone": "🏠"},
    {
        "nome": "Dados", 
        "icone": "📂", 
        # Aqui está a mágica: Uma lista de sub-itens dentro do item principal!
        "sub_itens": [
            {"nome": "Ler Dados", "url": "/ler_dados", "icone": "📥"},
            {"nome": "Processar Comissões", "url": "/comissao", "icone": "⚙️"}
        ]
    },
    {"nome": "Comissões", "url": "/comissao", "icone": "💰"},
    {"nome": "Contato", "url": "/contato", "icone": "✉️"},
    {"nome": "Relatórios", "url": "/relatorios", "icone": "📈"}
]

# ==========================================
# 2. ROTAS (Os "programas" do sistema)
# ==========================================

# Rota Principal (Home)
@app.route('/')
def home():
    # Passamos o menu=MENU_SISTEMA para o base.html desenhar a barra lateral
    return render_template('index.html', menu=MENU_SISTEMA)

# A nova rota para "Ler Dados"
@app.route('/ler_dados')
def ler_dados():
    return render_template('ler_dados.html', menu=MENU_SISTEMA)

# Rota de Comissões (Deixando preparada, já que está na lista do menu!)
@app.route('/comissao')
def comissao():
    return render_template('comissao.html', menu=MENU_SISTEMA)

# Rota de Contato
@app.route('/contato')
def contato():
    return render_template('contato.html', menu=MENU_SISTEMA)

# Rota de Relatórios
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html', menu=MENU_SISTEMA)

# ==========================================
# 3. INICIAR O SERVIDOR (Sempre no final!)
# ==========================================
if __name__ == '__main__':
    # Roda o servidor localmente para teste
    app.run(debug=True)