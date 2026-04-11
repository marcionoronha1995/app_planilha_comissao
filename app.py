from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import csv
import os
import io
from decimal import Decimal, ROUND_HALF_UP
import requests

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_desenvolvimento_seguro'

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
VERSAO_APP = "1.1.0" 

# Dicionário de traduções (Pode ser movido para um JSON externo no futuro)
TRADUCOES = {
    'pt': {
        'home': 'Home', 'dados': 'Dados', 'ler_dados': 'Ler Dados', 
        'processar': 'Processar Comissões', 'comissoes': 'Comissões', 
        'contato': 'Contato', 'relatorios': 'Relatórios', 'moeda': 'Moeda',
        'idioma': 'Idioma', 'vendedor': 'Nome do Vendedor', 'valor_venda': 'Valor da Venda',
        'taxa': 'Taxa (%)', 'comissao': 'Comissão', 'total_vendas': 'Total de Vendas',
        'comissoes_pagar': 'Comissões a Pagar', 'linhas': 'Linhas Processadas'
    },
    'en': {
        'home': 'Home', 'dados': 'Data', 'ler_dados': 'Read Data', 
        'processar': 'Process Commissions', 'comissoes': 'Commissions', 
        'contato': 'Contact', 'relatorios': 'Reports', 'moeda': 'Currency',
        'idioma': 'Language', 'vendedor': 'Salesperson', 'valor_venda': 'Sales Value',
        'taxa': 'Rate (%)', 'comissao': 'Commission', 'total_vendas': 'Total Sales',
        'comissoes_pagar': 'Commissions to Pay', 'linhas': 'Processed Rows'
    }
    ,
    'es': {
        'home': 'Inicio', 'dados': 'Datos', 'ler_dados': 'Leer Datos', 
        'processar': 'Procesar Comisiones', 'comissoes': 'Comisiones', 
        'contato': 'Contacto', 'relatorios': 'Informes', 'moeda': 'Moneda',
        'idioma': 'Idioma', 'vendedor': 'Vendedor', 'valor_venda': 'Valor de la Venta',
        'taxa': 'Tasa (%)', 'comissao': 'Comisión', 'total_vendas': 'Total de Ventas',
        'comissoes_pagar': 'Comisiones a Pagar', 'linhas': 'Líneas Procesadas'
    }
}

@app.context_processor
def inject_translate():
    """Injeta a função _() nos templates para tradução dinâmica"""
    def _(chave):
        idioma = session.get('idioma', 'pt')
        return TRADUCOES.get(idioma, TRADUCOES['pt']).get(chave, chave)
    return dict(_=_)

@app.template_filter('moeda')
def formato_moeda_br(valor, moeda_alvo=None):
    """Filtro para formatar valores convertidos e com símbolos"""
    if valor is None: valor = 0.0
    if moeda_alvo is None: moeda_alvo = session.get('moeda', 'BRL')
    
    # Taxas simples para demonstração
    taxas = {'BRL': 1.0, 'USD': 0.18, 'EUR': 0.17}
    simbolos = {'BRL': 'R$', 'USD': 'US$', 'EUR': '€'}
    
    valor_convertido = float(valor) * taxas.get(moeda_alvo, 1.0)
    simbolo = simbolos.get(moeda_alvo, 'R$')

    v_formatado = "{:,.2f}".format(valor_convertido)
    v_br = v_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
    return f"{simbolo} {v_br}"

MENU_SISTEMA = [
    {"nome": "home", "url": "/appcomissao/", "icone": "🏠"},
    {
        "nome": "dados", 
        "icone": "📂", 
        "sub_itens": [
            {"nome": "ler_dados", "url": "/appcomissao/ler_dados", "icone": "📥"},
            {"nome": "processar", "url": "/appcomissao/comissao", "icone": "⚙️"}
        ]
    },
    {"nome": "comissoes", "url": "/appcomissao/comissao", "icone": "💰"},
    {
        "nome": "moeda", 
        "icone": "💱", 
        "sub_itens": [
            {"nome": "Real (BRL)", "url": "/appcomissao/set_config/moeda/BRL", "icone": "🇧🇷"},
            {"nome": "Dólar (USD)", "url": "/appcomissao/set_config/moeda/USD", "icone": "🇺🇸"},
            {"nome": "Euro (EUR)", "url": "/appcomissao/set_config/moeda/EUR", "icone": "🇪🇺"}
        ]
    },
    {
        "nome": "idioma", 
        "icone": "🌐", 
        "sub_itens": [
            {"nome": "Português", "url": "/appcomissao/set_config/idioma/pt", "icone": "🇧🇷"},
            {"nome": "English", "url": "/appcomissao/set_config/idioma/en", "icone": "🇺🇸"},
            {"nome": "Español", "url": "/appcomissao/set_config/idioma/es", "icone": "🇪🇸"}
        ]
    },
    {"nome": "contato", "url": "/appcomissao/contato", "icone": "✉️"},
    {"nome": "relatorios", "url": "/appcomissao/relatorios", "icone": "📈"}
]

# ==========================================
# 2. LÓGICA DE NEGÓCIO (OBJETO DE SERVIÇO)
# ==========================================
class ComissaoService:
    """Gerencia o processamento, cálculos e validação das comissões."""
    
    # Usando Decimal para precisão financeira
    TAXA_COMISSAO = Decimal('0.10')  # Voltando para 10% conforme o objetivo inicial
    
    @staticmethod
    def _calcular_valores_linha(linha):
        """Calcula totais e comissão para uma linha do CSV."""
        try:
            # Conversão segura para Decimal
            def para_decimal(valor):
                if not valor or str(valor).strip() == "":
                    return Decimal('0.00')
                return Decimal(str(valor).replace(',', '.'))

            venda_total = (
                para_decimal(linha.get('VL_SETUP', 0)) + 
                para_decimal(linha.get('VL_TOTEM', 0)) + 
                para_decimal(linha.get('VL_LICENÇA', 0))
            )
            
            comissao = (venda_total * ComissaoService.TAXA_COMISSAO).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            return {
                "vendedor": linha.get('CLIENTE', 'Desconhecido'),
                "valor_venda": float(venda_total),
                "taxa": float(ComissaoService.TAXA_COMISSAO * 100),
                "valor_comissao": float(comissao)
            }
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _executar_processamento(leitor_csv):
        """Lógica centralizada para iterar no CSV e somar totais."""
        itens = []
        total_vendas = Decimal('0.00')
        total_comissoes = Decimal('0.00')

        for linha in leitor_csv:
            resultado = ComissaoService._calcular_valores_linha(linha)
            if resultado:
                itens.append(resultado)
                total_vendas += Decimal(str(resultado['valor_venda']))
                total_comissoes += Decimal(str(resultado['valor_comissao']))

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

def buscar_cotacao(moeda):
    """Faz a busca da cotação em tempo real via API externa."""
    try:
        # Utilizando o endpoint direto da AwesomeAPI para maior estabilidade
        url = f"https://economia.awesomeapi.com.br/last/{moeda}-BRL"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        dados = response.json()
        # A chave de retorno segue o padrão MOEDABRL (ex: USDBRL)
        chave = f"{moeda.upper()}BRL"
        if chave in dados:
            return float(dados[chave]['bid'])
        return None
    except Exception as e:
        print(f"Erro ao buscar cotação para {moeda}: {e}")
        return None

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
    # Inicialização de padrões na sessão
    if 'moeda' not in session: session['moeda'] = 'BRL'
    if 'idioma' not in session: session['idioma'] = 'pt'

    dados_processados = None
    if request.method == 'POST':
        modo_apresentacao = request.form.get('modo_apresentacao') == 'true'
        
        if modo_apresentacao:
            dados_processados = ComissaoService.carregar_dados_padrao()
        else:
            arquivo = request.files.get('arquivo_csv')
            dados_processados = ComissaoService.processar_arquivo_upload(arquivo)
            
    return render_template('comissao.html', menu=MENU_SISTEMA, versao=VERSAO_APP, dados=dados_processados)

@app.route('/get_cotacao/<moeda>')
def get_cotacao(moeda):
    """Rota que retorna o JSON da cotação para o frontend."""
    valor = buscar_cotacao(moeda.upper())
    return jsonify({"cotacao": valor})

@app.route('/set_config/<tipo>/<valor>')
def set_config(tipo, valor):
    """Rota genérica para configurar moeda ou idioma"""
    if tipo in ['moeda', 'idioma']:
        session[tipo] = valor
    return redirect(request.referrer or url_for('home'))

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