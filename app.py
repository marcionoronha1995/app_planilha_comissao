from flask import Flask, render_template

app = Flask(__name__)

# Rota Principal - É aqui que o Flask lê o seu index.html
@app.route('/')
def index():
    # O Flask procura automaticamente na pasta /templates
    return render_template('index.html')

if __name__ == '__main__':
    # Roda o servidor localmente para teste
    app.run(debug=True)
    
# A sua lista de configuração do menu (Fácil de manter!)
MENU_SISTEMA = [
    {"nome": "Home", "url": "/", "icone": "🏠"},
    {"nome": "Comissões", "url": "/comissao", "icone": "📊"},
    {"nome": "Contato", "url": "/contato", "icone": "✉️"},
    {"nome": "Relatórios", "url": "/relatorios", "icone": "📈"}
    
    
]

def home():
    # Passamos a lista MENU_SISTEMA para o HTML usar
    return render_template('index.html', menu=MENU_SISTEMA)

@app.route('/contato')
def contato():
    return render_template('contato.html', menu=MENU_SISTEMA)

if __name__ == '__main__':
    app.run(debug=True)

# Rota para o novo programa de Relatórios
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')