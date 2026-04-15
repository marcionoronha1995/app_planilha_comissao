from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import csv
import os
import io
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import requests
import time

# Cache global para evitar excesso de chamadas à API (expira em 5 minutos)
CACHE_TAXAS = {}

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_desenvolvimento_seguro'

# ==========================================
# 1. CONFIGURAÇÕES GERAIS
# ==========================================
VERSAO_APP = "1.2.0" 

# Dicionário de traduções (Pode ser movido para um JSON externo no futuro)
TRADUCOES = {
    'pt': {
        'home': 'Home', 'dados': 'Dados', 'ler_dados': 'Ler Dados', 
        'processar': 'Processar Comissões', 'comissoes': 'Comissões', 
        'contato': 'Contato', 'relatorios': 'Relatórios', 'moeda': 'Moeda',
        'idioma': 'Idioma', 'vendedor': 'Nome do Vendedor', 'valor_venda': 'Valor da Venda',
        'taxa': 'Taxa (%)', 'comissao': 'Comissão', 'total_vendas': 'Total de Vendas',
        'comissoes_pagar': 'Comissões a Pagar', 'linhas': 'Linhas Processadas'
        , 'instrucao_inicial': 'Selecione uma opção no menu lateral para começar.',
        'instrucao_upload': 'Faça o upload da sua planilha de vendas (formato CSV) para o sistema.',
        'dados_padrao_apresentacao': 'Use os dados padrão para apresentação',
        'btn_carregar_padrao': 'Carregar e Processar Dados Padrão Apresentação',
        'confirmar_carregamento': 'Confirmar Carregamento',
        'msg_modal_confirmacao': 'Você está prestes a carregar os dados de demonstração do sistema. Isso substituirá as visualizações atuais. Deseja continuar?',
        'sim_carregar_padrao_btn': 'Sim, carregar dados padrão',
        'selecione_csv': 'Selecione o arquivo CSV',
        'apenas_csv': 'Apenas arquivos com extensão .csv são aceitos.',
        'btn_carregar_arquivo': 'Carregar e Processar Dados',
        'resultados_csv': 'Resultados do processamento da planilha de vendas.',
        'cotacao_tempo_real': 'Cotação em Tempo Real (BRL)',
        'moeda_alvo': 'Moeda Alvo',
        'cambio_atual': 'Câmbio Atual (R$)',
        'aguardando': 'Aguardando...',
        'dados_carregados_via': 'Dados carregados via',
        'nenhum_dado': 'Nenhum dado processado ainda. Vá em "Ler Dados" para enviar um arquivo CSV.',
        'contato_titulo': 'Entre em Contato', 
        'contato_desc': 'Esta é uma tela de contato. Sinta-se à vontade para enviar uma mensagem.',
        'label_nome': 'Nome', 'label_email': 'E-mail', 'label_telefone': 'Telefone', 
        'label_mensagem': 'Sua Mensagem', 'btn_enviar': 'Enviar Mensagem',
        'placeholder_nome': 'Digite seu nome completo',
        'placeholder_email': 'exemplo@email.com',
        'placeholder_telefone': '(00) 99999-9999',
        'placeholder_mensagem': 'Como podemos ajudar você hoje?',
        'msg_sucesso': 'Obrigado, {nome}! Recebemos sua mensagem e entraremos em contato em breve.',
        'msg_erro_validacao': 'Dados inválidos ou e-mail malformatado.',
        'msg_erro_interno': 'Ocorreu um erro interno ao enviar.',
        'relatorios_titulo': 'Programa de Relatórios', 'relatorios_desc': 'Bem-vindo à tela de relatórios. Aqui vamos colocar os gráficos no futuro.'
    },
    'en': {
        'home': 'Home', 'dados': 'Data', 'ler_dados': 'Read Data', 
        'processar': 'Process Commissions', 'comissoes': 'Commissions', 
        'contato': 'Contact', 'relatorios': 'Reports', 'moeda': 'Currency',
        'idioma': 'Language', 'vendedor': 'Salesperson', 'valor_venda': 'Sales Value',
        'taxa': 'Rate (%)', 'comissao': 'Commission', 'total_vendas': 'Total Sales',
        'comissoes_pagar': 'Commissions to Pay', 'linhas': 'Processed Rows'
        , 'instrucao_inicial': 'Select an option in the sidebar to start.',
        'instrucao_upload': 'Upload your sales spreadsheet (CSV format) to the system.',
        'dados_padrao_apresentacao': 'Use default data for presentation',
        'btn_carregar_padrao': 'Load and Process Default Presentation Data',
        'confirmar_carregamento': 'Confirm Loading',
        'msg_modal_confirmacao': 'You are about to load the system demonstration data. This will replace the current views. Do you want to continue?',
        'sim_carregar_padrao_btn': 'Yes, load default data',
        'selecione_csv': 'Select CSV file',
        'apenas_csv': 'Only files with .csv extension are accepted.',
        'btn_carregar_arquivo': 'Load and Process Data',
        'resultados_csv': 'Sales spreadsheet processing results.',
        'cotacao_tempo_real': 'Real-Time Quote (BRL)',
        'moeda_alvo': 'Target Currency',
        'cambio_atual': 'Current Exchange (R$)',
        'aguardando': 'Waiting...',
        'dados_carregados_via': 'Data loaded via',
        'nenhum_dado': 'No data processed yet. Go to "Read Data" to upload a CSV file.',
        'contato_titulo': 'Contact Us', 
        'contato_desc': 'This is a contact screen. Feel free to send a message.',
        'label_nome': 'Full Name', 'label_email': 'Email Address', 'label_telefone': 'Phone Number', 
        'label_mensagem': 'Your Message', 'btn_enviar': 'Send Message',
        'placeholder_nome': 'Enter your full name',
        'placeholder_email': 'example@email.com',
        'placeholder_telefone': '+1 (000) 000-0000',
        'placeholder_mensagem': 'How can we help you today?',
        'msg_sucesso': 'Thank you, {nome}! We have received your message and will get back to you soon.',
        'msg_erro_validacao': 'Invalid data or malformed email.',
        'msg_erro_interno': 'An internal error occurred while sending.',
        'relatorios_titulo': 'Reports Program', 'relatorios_desc': 'Welcome to the reports screen. This is where we will put the charts in the future.'
    }
    ,
    'es': {
        'home': 'Inicio', 'dados': 'Datos', 'ler_dados': 'Leer Datos', 
        'processar': 'Procesar Comisiones', 'comissoes': 'Comisiones', 
        'contato': 'Contacto', 'relatorios': 'Informes', 'moeda': 'Moneda',
        'idioma': 'Idioma', 'vendedor': 'Vendedor', 'valor_venda': 'Valor de la Venta',
        'taxa': 'Tasa (%)', 'comissao': 'Comisión', 'total_vendas': 'Total de Ventas',
        'comissoes_pagar': 'Comisiones a Pagar', 'linhas': 'Líneas Procesadas'
        , 'instrucao_inicial': 'Seleccione una opción en el menú lateral para comenzar.',
        'instrucao_upload': 'Cargue su hoja de cálculo de ventas (formato CSV) al sistema.',
        'dados_padrao_apresentacao': 'Utilice los datos predeterminados para la presentación',
        'btn_carregar_padrao': 'Cargar y Procesar Datos de Presentación Predeterminados',
        'confirmar_carregamento': 'Confirmar Carga',
        'msg_modal_confirmacao': 'Está a punto de cargar los datos de demostración del sistema. Esto reemplazará las vistas actuales. ¿Desea continuar?',
        'sim_carregar_padrao_btn': 'Sí, cargar datos predeterminados',
        'selecione_csv': 'Seleccionar archivo CSV',
        'apenas_csv': 'Sólo se aceptan archivos con extensión .csv.',
        'btn_carregar_arquivo': 'Cargar y Procesar Datos',
        'resultados_csv': 'Resultados del procesamiento de la hoja de cálculo de ventas.',
        'cotacao_tempo_real': 'Cotización en Tiempo Real (BRL)',
        'moeda_alvo': 'Moneda de Destino',
        'cambio_atual': 'Cambio Actual (R$)',
        'aguardando': 'Esperando...',
        'dados_carregados_via': 'Datos cargados vía',
        'nenhum_dado': 'Aún no se han procesado datos. Vaya a "Ler Dados" para cargar un archivo CSV.',
        'contato_titulo': 'Contáctenos', 
        'contato_desc': 'Esta es una pantalla de contacto. Siéntase libre de enviar un mensaje.',
        'label_nome': 'Nombre Completo', 'label_email': 'Correo electrónico', 'label_telefone': 'Teléfono', 
        'label_mensagem': 'Su Mensaje', 'btn_enviar': 'Enviar Mensaje',
        'placeholder_nome': 'Escriba su nombre completo',
        'placeholder_email': 'ejemplo@correo.com',
        'placeholder_telefone': '+34 000 000 000',
        'placeholder_mensagem': '¿Cómo podemos ayudarle hoy?',
        'msg_sucesso': '¡Gracias, {nome}! Hemos recibido su mensaje y nos pondremos en contacto en breve.',
        'msg_erro_validacao': 'Datos inválidos o correo malformado.',
        'msg_erro_interno': 'Ocurrió un error interno al enviar.',
        'relatorios_titulo': 'Programa de Informes', 'relatorios_desc': 'Bienvenido a la pantalla de informes. Aquí es donde pondremos los gráficos en el futuro.'
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
    if valor is None: valor = 0
    if moeda_alvo is None: moeda_alvo = session.get('moeda', 'BRL')
    
    # Obter taxa real via nossa função de busca
    taxa_conversao = 1.0
    if moeda_alvo != 'BRL':
        valor_venda_em_brl = buscar_cotacao(moeda_alvo)
        if valor_venda_em_brl:
            taxa_conversao = 1.0 / valor_venda_em_brl

    simbolos = {'BRL': 'R$', 'USD': 'US$', 'EUR': '€'}
    valor_convertido = float(valor) * taxa_conversao
    simbolo = simbolos.get(moeda_alvo, 'R$')

    v_formatado = "{:,.2f}" if moeda_alvo != 'BTC' else "{:,.8f}"
    v_formatado = v_formatado.format(valor_convertido)
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
    
    @staticmethod
    def para_decimal(valor):
        """Converte strings de moeda para Decimal tratando separadores brasileiros."""
        if not valor or str(valor).strip() == "":
            return Decimal('0.00')
        v = str(valor).strip()
        if ',' in v and '.' in v: # Formato 1.234,56
            v = v.replace('.', '').replace(',', '.')
        return Decimal(v.replace(',', '.'))

    @staticmethod
    def _calcular_valores_linha(linha, taxa):
        """Calcula totais e comissão para uma linha do CSV."""
        try:
            venda_total = (
                ComissaoService.para_decimal(linha.get('VL_SETUP', 0)) + 
                ComissaoService.para_decimal(linha.get('VL_TOTEM', 0)) + 
                ComissaoService.para_decimal(linha.get('VL_LICENÇA', 0))
            )
            
            comissao = (venda_total * taxa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            return {
                "vendedor": linha.get('CLIENTE', 'Desconhecido'),
                "valor_venda": float(venda_total),
                "taxa": float(taxa * 100),
                "valor_comissao": float(comissao)
            }
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _executar_processamento(leitor_csv, taxa):
        """Lógica centralizada para iterar no CSV e somar totais."""
        itens = []
        total_vendas = Decimal('0.00')
        total_comissoes = Decimal('0.00')

        for linha in leitor_csv:
            resultado = ComissaoService._calcular_valores_linha(linha, taxa)
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
    def carregar_dados_padrao(taxa):
        """Lê o arquivo local dados_planilha.csv."""
        caminho_arquivo = os.path.join(os.path.dirname(__file__), "dados_planilha.csv")
        
        if not os.path.exists(caminho_arquivo):
            return {"erro": "Arquivo padrão não encontrado."}

        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            leitor = csv.DictReader(f)
            dados = ComissaoService._executar_processamento(leitor, taxa)
            dados['origem'] = "Arquivo Padrão (Local)"
            return dados

    @staticmethod
    def processar_arquivo_upload(arquivo, taxa):
        """Processa o arquivo enviado via formulário."""
        if not arquivo or arquivo.filename == '':
            return None
        
        # Transforma o stream do upload em um formato que o csv.DictReader entenda
        stream = io.StringIO(arquivo.stream.read().decode("UTF8"), newline=None)
        leitor = csv.DictReader(stream)
        
        dados = ComissaoService._executar_processamento(leitor, taxa)
        dados['origem'] = f"Upload: {arquivo.filename}"
        return dados

def buscar_cotacao(moeda):
    """Faz a busca da cotação em tempo real via API externa."""
    moeda = moeda.upper()
    agora = time.time()
    
    # Verifica se temos a cotação no cache e se tem menos de 5 minutos
    if moeda in CACHE_TAXAS:
        valor, timestamp = CACHE_TAXAS[moeda]
        if agora - timestamp < 300:
            return valor

    try:
        url = f"https://economia.awesomeapi.com.br/last/{moeda}-BRL"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        dados = response.json()
        chave = f"{moeda}BRL"
        if chave in dados and 'bid' in dados[chave]:
            valor = float(dados[chave]['bid'])
            if valor > 0:
                CACHE_TAXAS[moeda] = (valor, agora)
                return valor
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
    if 'taxa' not in session: session['taxa'] = '10'

    # Converte a taxa da sessão para Decimal (ex: "10" vira 0.10)
    valor_taxa = Decimal(session.get('taxa', '10')) / Decimal('100')

    dados_processados = None
    if request.method == 'POST':
        modo_apresentacao = request.form.get('modo_apresentacao') == 'true'
        
        if modo_apresentacao:
            dados_processados = ComissaoService.carregar_dados_padrao(taxa=valor_taxa)
        else:
            arquivo = request.files.get('arquivo_csv')
            dados_processados = ComissaoService.processar_arquivo_upload(arquivo, taxa=valor_taxa)
            
    return render_template('comissao.html', menu=MENU_SISTEMA, versao=VERSAO_APP, dados=dados_processados)

@app.route('/get_cotacao/<moeda>')
def get_cotacao(moeda):
    """Rota que retorna o JSON da cotação para o frontend."""
    valor = buscar_cotacao(moeda.upper())
    return jsonify({"cotacao": valor})

@app.route('/set_config/<tipo>/<valor>')
def set_config(tipo, valor):
    """Rota genérica para configurar moeda ou idioma"""
    if tipo in ['moeda', 'idioma', 'taxa']:
        session[tipo] = valor
    return redirect(request.referrer or url_for('home'))

@app.route('/contato')
def contato():
    return render_template('contato.html', menu=MENU_SISTEMA, versao=VERSAO_APP)

@app.route('/enviar_contato', methods=['POST'])
def enviar_contato():
    """Recebe e processa os dados do formulário de contato"""
    idioma = session.get('idioma', 'pt')
    trad = TRADUCOES.get(idioma, TRADUCOES['pt'])
    try:
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        mensagem = request.form.get('mensagem')
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Validação básica de servidor
        if not nome or not email or "@" not in email:
            flash(trad['msg_erro_validacao'], "danger")
            return redirect(url_for('contato'))

        # Salva o contato em um arquivo CSV local para persistência
        caminho_contatos = os.path.join(os.path.dirname(__file__), "contatos_recebidos.csv")
        file_exists = os.path.isfile(caminho_contatos)
        
        with open(caminho_contatos, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Data/Hora', 'Nome', 'Email', 'Telefone', 'Mensagem']) # Cabeçalho
            writer.writerow([data_hora, nome, email, telefone, mensagem])

        print(f"[{data_hora}] Novo contato: {nome} <{email}>")
        
        flash(trad['msg_sucesso'].format(nome=nome), "success")
        return redirect(url_for('contato'))

    except Exception as e:
        print(f"Erro ao processar contato: {e}")
        flash(trad['msg_erro_interno'], "danger")
        return redirect(url_for('contato'))

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