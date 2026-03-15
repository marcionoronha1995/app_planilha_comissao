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

@app.route('/')
def index(): # <-- O url_for procura este nome aqui
    return render_template('index.html')    