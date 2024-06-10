from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
from model import db, Usuario, Agenda, Barbearia, PrecoServico, Servico, init_db
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from scripts.scripts import calcular_horarios_disponiveis, calcular_horarios_indisponiveis, converter_duracao_para_minutos, enviar_email_recuperar_senha, endereco_cliente_simplificado
from scripts.geolocalizacao import find_nearby_establishments, obter_barbearia_e_distancia
import random as rd
from datetime import datetime
from geopy.geocoders import Nominatim


app = Flask(__name__)

# Configuração da chave secreta para a aplicação Flask
app.config['SECRET_KEY'] = 'A123S456D789'

# Configuração da URI do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/bdnaregua'

# Desativa a sinalização de modificações de objetos para economizar recursos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados com a aplicação Flask
init_db(app)

# Configuração do gerenciador de login
login_manager = LoginManager(app)

# Define a rota de login
login_manager.login_view = 'login'

# Define a mensagem que aparecerá caso o usuário precise fazer o login
login_manager.login_message = 'Faça Login Ou Cadastre-se Para Acessar'

# Define a categoria da mensagem de login
login_manager.login_message_category = 'error'
    
#Carregar um usuário da sessão.
@login_manager.user_loader
def load_user(user_id):
    
    # Esta função é chamada pelo Flask-Login para carregar um usuário da sessão.
    
    # Aqui, estamos usando o 'user_id', que é o identificador do usuário na sessão,
    # para encontrar o usuário correspondente no banco de dados.
    
    # Query para encontrar o usuário pelo CPF (ou outro identificador único).
    user = Usuario.query.filter_by(cpf=user_id).first()
    
    # Retorna o usuário encontrado ou 'None' se não for encontrado.
    return user


# Filtro customizado para formatar a hora
def format_time(value, format='%H:%M'):
    if value is None:
        return ""
    return value.strftime(format)

# Registrar o filtro customizado no ambiente Jinja2 do Flask
app.jinja_env.filters['format_time'] = format_time


# ------------------------------------------------ LOGIN ------------------------------------------------
# Essa função é uma rota onde renderiza o template entrar.html(página de login) e 
# caso houver algum parâmetro next, redirecionar para a rota do parametro next após o login.
@app.route('/login')
def login():
    global parametro_next
    parametro_next = request.args.get('next')
    if parametro_next:
        print('Parametro Next:', parametro_next)
    return render_template('entrar.html')


# Esta função é uma rota Flask que recebe os dados de login de um formulário HTML via método POST.
@app.route('/coletar-login', methods=['POST'])
def coletar_login():

    # Obtém o nome de usuário e senha do formulário enviado.
    login = request.form['username']
    password = request.form['password']

    # Converte os dados para strings (caso não estejam em string).
    login = str(login)
    password = str(password)
    
    # Verifica se o usuário existe no banco de dados pelo email ou telefone.
    usuario_email = Usuario.query.filter_by(email=login).first()
    usuario_telefone = Usuario.query.filter_by(telefone=login).first()
    
    # Se o usuário existe pelo email ou telefone, prossegue com a autenticação.
    if usuario_email or usuario_telefone:
        # Define o usuário com base no email ou telefone encontrado.
        usuario = usuario_email if usuario_email else usuario_telefone
        
        # Verifica se a senha fornecida corresponde à senha do usuário.
        if usuario.senha == password:
            # Autentica o usuário.
            login_user(usuario)
            
            # Verifica se há um parâmetro 'next' na URL para redirecionar após o login.
            if parametro_next:
                return redirect(parametro_next)
            else:            
                return redirect(url_for('barber'))
            
        else:
            # Se a senha estiver incorreta, exibe uma mensagem de erro e redireciona para a página de login.
            flash('Usuário ou senha incorreta', 'error')
            return redirect(url_for('login'))
    else:
        # Se o usuário não existir, exibe uma mensagem de erro e redireciona para a página de login.
        flash('Usuário incorreto', 'error')
        return redirect(url_for('login'))


# ------------------------------------------------ CADASTRO ------------------------------------------------
#Rota cadastrar, apenas renderiza o template cadastrar.html
@app.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar.html')

# Esta função é uma rota Flask que recebe os dados de cadastro para cadastrar um CLIENTE 
@app.route('/coletar-cadastro', methods=['POST'])
def coletar_cadastro():
    
    # Obtém os dados do formulário enviado.
    nomeUsuario = request.form['nomeCompleto']
    cpf = request.form['cpf']
    telefoneCliente = request.form['telefone']
    email = request.form['emailCliente']
    ruaCliente = request.form['ruaCliente']  # Rua do endereço da barbearia
    numeroEnderecoCliente = request.form['numeroCliente']  # Número do endereço da barbearia
    bairroCliente = request.form['bairroCliente']  # Bairro do endereço da barbearia
    cepCliente = request.form['cepCliente']  # CEP do endereço da barbearia
    cidadeCliente = request.form['cidadeCliente']  # Cidade do endereço da barbearia
    estadoCliente = request.form['estadoCliente']  # Estado do endereço da barbearia
    senha_cliente1 = request.form['senhaCliente1']
    senha_cliente2 = request.form['senhaCliente2']
    
    try:
        temBarbearia = request.form['tem_barbearia']
    except:
        flash('Selecione se você é uma barbearia.', 'error')
        return redirect(url_for('cadastrar'))
    
    # Coleta os dados do formulário caso o cliente escolher a opção de barbeiro
    nomeBarbearia = request.form['nomeBarbearia']  # Nome da barbearia
    telefoneBarbearia = request.form['telefone']  # Telefone da barbearia
    qtdBarbeiros = request.form['qtdBarbeiros'] # Quantidade de barbeiros disponíveis.
    rua = request.form['rua']  # Rua do endereço da barbearia
    numeroEndereco = request.form['numero']  # Número do endereço da barbearia
    bairro = request.form['bairro']  # Bairro do endereço da barbearia
    cep = request.form['cep']  # CEP do endereço da barbearia
    cidade = request.form['cidade']  # Cidade do endereço da barbearia
    estado = request.form['estado']  # Estado do endereço da barbearia
    horaInicio = request.form['horario_abertura_sim']  # Horário de abertura da barbearia
    horaFim = request.form['horario_fechamento_sim']  # Horário de fechamento da barbearia
    senha_barbearia1 = request.form.get('senha1')
    senha_barbearia2 = request.form.get('senha2')
    
    # Verifica se algum campo obrigatório está em branco ou inválido.
    if not all([nomeUsuario, telefoneCliente, email, cpf, ruaCliente, numeroEnderecoCliente, bairroCliente, cepCliente, cidadeCliente, estadoCliente]):
        flash('Houve algum campo em branco.', 'error')
        return redirect(url_for('cadastrar'))
    
    elif temBarbearia == 'nao' and not all([senha_cliente1, senha_cliente2]):
        flash('O campo de senha esta em branco.', 'error')
        return redirect(url_for('cadastrar'))
    
    elif temBarbearia == 'sim' and not all([nomeBarbearia, telefoneBarbearia, qtdBarbeiros, rua, numeroEndereco, bairro, cep, cidade, estado, horaInicio, horaFim]):
        flash('Houve algum campo em branco', 'error')
        return redirect(url_for('cadastrar'))
        
    elif temBarbearia == 'sim' and not all([senha_barbearia1, senha_barbearia2]):
        flash('O campo de senha esta em branco.', 'error')
        return redirect(url_for('cadastrar'))
        
    elif temBarbearia == 'sim' and qtdBarbeiros == '0':
        flash('Quantidade de barbeiros inválida.', 'error')
        return redirect(url_for('cadastrar'))
    
    
    if temBarbearia == 'nao':
        # Verifica se as senhas fornecidas coincidem e cria o usuario.
            if str(senha_cliente1) == str(senha_cliente2):
                print('SENHA:', senha_barbearia1, senha_barbearia2)
                # Formata os dados antes de criar um novo usuário.
                nomeUsuario = nomeUsuario.capitalize()
                email = email.lower()
                enderecoCliente = f'{ruaCliente}, {numeroEnderecoCliente}, {bairroCliente}, {cidadeCliente}, {estadoCliente}'
                
                # Cria um novo objeto de usuário com os dados fornecidos.
                novo_usuario = Usuario(cpf=cpf, nomeUsuario=nomeUsuario, email=email, telefone=telefoneCliente, enderecoCliente = enderecoCliente , senha=senha_cliente1, barbeiro = False, idBarbearia_fk = None)
                # Adiciona o novo usuário ao banco de dados.
                db.session.add(novo_usuario)
                db.session.commit()
                
                print('Parabéns!! Novo cliente cadastrado Na Régua!\n')
                print(f'''
            INFORMAÇÕES DO USUARIO:
        Nome do usuario: {nomeUsuario}
        email: {email}
        cpf: {cpf}
        telefone: {telefoneCliente}
        senha: {senha_cliente1, senha_barbearia1}
        ''')
                return redirect(url_for('login'))
            
            
            else:
                flash('As senhas não coincidem, tente novamente.','error')
                # Redireciona de volta para a página de cadastro.
                return redirect(url_for('cadastrar'))
            
            # Se o usuario for uma barbearia, vamos criar sua barbearia.
    if temBarbearia == 'sim':
        
        if str(senha_barbearia1) == str(senha_barbearia2):
            # Constrói o endereço completo
            endereco = f'{rua}, {numeroEndereco}, {bairro}, {cidade}, {estado}'
            enderecoCliente = f'{ruaCliente}, {numeroEnderecoCliente}, {bairroCliente}, {cidadeCliente}, {estadoCliente}'
            
            novo_usuario = Usuario(cpf=cpf, nomeUsuario=nomeUsuario, email=email, telefone=telefoneCliente, enderecoCliente = enderecoCliente , senha=senha_barbearia1, barbeiro = False, idBarbearia_fk = None)
            # Adiciona o novo usuário ao banco de dados.
            db.session.add(novo_usuario)
            db.session.commit()
            
            # Cria uma nova instância de 'Barbearia' com os dados coletados
            novoBarbeiro = Barbearia(nomeBarbearia=nomeBarbearia, telefone=telefoneBarbearia, enderecoBarbearia=endereco, qtdBarbeiros = qtdBarbeiros, horaInicio=horaInicio, horaFim=horaFim, disponibilidade = 'ativo')
            
            # Adiciona a nova barbearia à sessão do banco de dados e confirma a transação
            db.session.add(novoBarbeiro)
            db.session.commit()

            # Atualiza o usuário para indicar que ele é barbeiro e associa a barbearia recém-criada.
            novo_usuario.barbeiro = True
            novo_usuario.idBarbearia_fk = novoBarbeiro.idBarbearia
            db.session.commit()
            
            print('Parabens!! Um novo barbeiro foi cadastrado no Ná Régua.')
            print(f'''
    INFORMAÇÕES DA BARBEARIA:
Barbearia: {nomeBarbearia}
Número: {telefoneBarbearia}
Endereço: {endereco}
Qtd. de barbeiros: {qtdBarbeiros}
horario de abertura: {horaInicio}
horario de fechamento: {horaFim}
''')
            # Redireciona para a página inicial após o cadastro bem-sucedido.
            return redirect(url_for('login'))
    
        else:
            flash('As senhas não coincidem. Tente novamente.','error')
            # Redireciona de volta para a página de cadastro.
            return redirect(url_for('cadastrar'))


# ------------------------------------------------ Esqueci minha senha -------------------------------------
#Essa função apenas exibe o template esqueci_minha_Senha.html
@app.route('/esq-senha')
def esq_senha():
    return render_template('esqueci_minha_senha.html')

# Esta função é uma rota Flask que recebe os dados de esqueci minha senha(template renderizado na função anterior).
@app.route('/coletar_email_recuperar', methods=['POST'])
def coletar_email_recuperar():
    # Define as variáveis como globais para poderem ser acessadas fora da função.
    global email
    global codigo
    global dicionario_mudar_senha
    global codCliente
    
    # Obtém o email fornecido pelo usuário no formulário.
    email = request.form['email']
    
    # Gera um código de recuperação de senha aleatório de seis dígitos.
    codigo = rd.randint(100000, 999999)
    
    # Cria um dicionário onde a chave é o email e o valor é o código de recuperação.
    dicionario_mudar_senha = {f'{email}': f'{codigo}'}
    
    # Verifica se o usuário com o email fornecido está cadastrado.
    usuario_email = Usuario.query.filter_by(email=email).first()
    
    if usuario_email:
        # Gera um código de cliente aleatório para a recuperação da senha.
        codCliente = rd.randint(1000, 9999)
        
        # Envia um email com o código de recuperação para o email fornecido.
        enviar_email_recuperar_senha(email, codigo)
        
        # Redireciona para a página de inserção do token.
        return redirect(url_for('token_acess', codCliente=codCliente))
    else:
        # Se o email não estiver cadastrado, exibe uma mensagem de erro e redireciona para a página de esqueci minha senha.
        flash('Usuário não cadastrado.', 'error')
        return redirect(url_for('esq_senha'))
        
#Essa função apenas renderiza o template token_de_acesso.html. 
#Essa rota recebe como parametro a variavel codCliente, que é um codigo de segurança passado na url,
#Exemplo: www.recuperar.com/token/<123456>.
@app.route('/token/<codCliente>')
def token_acess(codCliente):
    print(codigo)
    flash("Te enviamos um código por e-mail. Descreva-o abaixo.", 'sucess')
    return render_template('token_de_acesso.html')

# Essa rota recebe como método POST os token's informados pelo usuario no formulario da pagina do template
# renderizado na rota anterior.
@app.route('/coletar_token', methods=['POST'])
def coletar_token():
    # Recebe os tokens do formulário.
    token1 = request.form['token1']
    token2 = request.form['token2']
    token3 = request.form['token3']
    token4 = request.form['token4']
    token5 = request.form['token5']
    token6 = request.form['token6']
    
    # Concatena os tokens para formar o token completo.
    token = f'{token1}{token2}{token3}{token4}{token5}{token6}'

    # Verifica se o token fornecido está presente no dicionário de tokens válidos.
    if token in dicionario_mudar_senha.values(): 
        # Se o token estiver presente, redireciona para a rota de criação de senha.
        print('Token Autorizado.')
        return redirect(url_for('criar_senha'))
    
    else:
        # Se o token estiver incorreto, exibe uma mensagem de erro e redireciona de volta para a página de inserção de token.
        flash('Código incorreto.', 'error')
        return redirect(url_for('token_acess', codCliente=codCliente))

#Essa função é uma rota flask que apenas renderiza a pagina criar_senha_nova.html
@app.route('/criar-senha')
def criar_senha():
    return render_template('criar_senha_nova.html')

#Essa função é uma rota flask que recebe como método post as novas senhas escritas pelo usuario e
#Atualiza no banco de dados sua nova senha.
@app.route('/coletar_nova_senha', methods=['POST'])
def coletar_nova_senha():
    # Recebe as novas senhas do formulário.
    senha = request.form['senha']
    confirmarSenha = request.form['confirmarSenha']

    # Verifica se as senhas coincidem.
    if senha == confirmarSenha:
        # Encontra o usuário com base no email (assumindo que a variável 'email' está definida em outro lugar).
        usuario = Usuario.query.filter_by(email=email).first()    

        # Atualiza a senha do usuário.
        usuario.senha = senha

        # Comita as mudanças no banco de dados.
        db.session.commit()

        # Redireciona para a página de login após a alteração bem-sucedida.
        flash("Senha alterada com sucesso!", 'success')
        return redirect(url_for('login'))
    else:
        # Se as senhas não coincidirem, exibe uma mensagem de erro e redireciona de volta para a página de criação de senha.
        flash('As senhas não coincidem. Tente novamente.', 'error')
        return redirect(url_for('criar_senha'))


# ------------------------------------------------ Página Inicial ------------------------------------------
# Define a rota '/home-barbearia' e a rota raiz '/' para a função 'barber'
@app.route('/home-barbearia')
@app.route('/')
def barber():
    
    # Verifica se o usuário atual está autenticado
    if current_user.is_authenticated:
        # Converte o valor do campo 'barbeiro' do usuário atual para inteiro
        lista_barbearias = []
        barbeiro = int(current_user.barbeiro)
        barbearia = current_user.idBarbearia_fk
        print('ID BARBER:', barbearia)
        usuario = Usuario.query.filter_by(idUsuario=current_user.idUsuario).first()
        
        if usuario is None:
                raise ValueError("Usuário não encontrado no banco de dados")
            
        if barbearia:
            nome = Barbearia.query.filter_by(idBarbearia = barbearia).first()
            nome = nome.nomeBarbearia
            print(nome)
            
        else:
            print('Caiu aqui')
            nome = usuario.nomeUsuario
            print('Nome do usuario:', nome)
    
        # Renderiza o template 'sistema-homepage.html', passando o valor de 'barbeiro' e a lista de todos os serviços
        barbearias = Barbearia.query.all()
        
        if not barbearias:
            flash('Barbearias indisponíveis em sua região', 'error')
        
        endereco_simplificado = session.get('endereco_simplificado', None)
        
        if endereco_simplificado:
            print('Endereço Geolocalização:', endereco_simplificado)

            if usuario is None:
                raise ValueError("Usuário não encontrado no banco de dados")

            for barbearia in barbearias:
                if barbearia.disponibilidade == 'ativo':
                    lista_barbearias.append(barbearia)

            barbearias_e_distancias = obter_barbearia_e_distancia(lista_barbearias, endereco_simplificado)
            
            if not barbearias_e_distancias:
                flash('Nenhuma barbearia encontrada proxima a você.', 'error')
                
            print('Nome da Barbearia:', nome)
            return render_template('sistema-homepage.html', barbeiro=barbeiro, servicos=Servico.query.all(), lista_barbearias_proximas=barbearias_e_distancias, enderecoCliente = endereco_simplificado, nome_barbearia = nome, usuario = nome)
        
        else:
            
            print('Endereço Geolocalização:', usuario.enderecoCliente)
            
            for barbearia in barbearias:
                if barbearia.disponibilidade == 'ativo':
                    lista_barbearias.append(barbearia)
                    
            barbearias_e_distancias = obter_barbearia_e_distancia(lista_barbearias, usuario.enderecoCliente)
                
            print('Nome da barbearia:', nome)
            return render_template('sistema-homepage.html', barbeiro=barbeiro, servicos=Servico.query.all(), lista_barbearias_proximas=barbearias_e_distancias, enderecoCliente = usuario.enderecoCliente, nome_barbearia = nome, usuario = nome)
        
    else:
        barbearias = Barbearia.query.all()
        
        endereco_simplificado = session.get('endereco_simplificado', None)
        if endereco_simplificado:
            print('Endereço Geolocalização:', endereco_simplificado)
            barbearias_e_distancias = obter_barbearia_e_distancia(barbearias, endereco_simplificado)
            
            if not barbearias_e_distancias:
                flash('Barbearias indisponíveis em sua região.', 'error')    
                return render_template('sistema-homepage.html', servicos=Servico.query.all(), enderecoCliente = endereco_simplificado)
            
            else:
                return render_template('sistema-homepage.html', lista_barbearias_proximas=barbearias_e_distancias, servicos=Servico.query.all(), enderecoCliente = endereco_simplificado)
            
        else:
            print('Nenhum endereço na geolocalização.')
            endereco_simplificado = None
            return render_template('sistema-homepage.html', servicos=Servico.query.all(), enderecoCliente = endereco_simplificado)    


@app.route('/get-address', methods=['POST'])
def get_address():
    data = request.json
    latitude = data['latitude']
    longitude = data['longitude']
    
    geolocator = Nominatim(user_agent="wuwigEZtJAkea4q4aiQdP9s2YFHza389EITd-oLdCTI")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    
    address = location.address
    enderecoCliente = address
    
    address_parts = location.raw['address']
    
    endereco_simplificado = endereco_cliente_simplificado(address_parts)
    
    barbearias = Barbearia.query.all()
    
    lista_barbearias_proximas = []
    lista_distancias_barbearia = []
    
    if barbearias:
        for barbearia in barbearias:
            print(endereco_simplificado)
            barbearias_dentro_de_2_km = find_nearby_establishments(endereco_simplificado, [barbearia.enderecoBarbearia for barbearia in barbearias])
            
            if barbearias_dentro_de_2_km:
            
                if not isinstance(barbearias_dentro_de_2_km, list):
                    barbearias_dentro_de_2_km = [barbearias_dentro_de_2_km]
                
                for establishment in barbearias_dentro_de_2_km:
                    if isinstance(establishment, dict):
                        address = establishment.get('address')
                        distance_km = establishment.get('distance_km')
                        if address and distance_km is not None:
                            print(f"Endereço: {address} - Distância: {distance_km:.2f} km")
                            distancia = "{:.2f}".format(distance_km)
                            if normalize_address(address) == normalize_address(barbearia.enderecoBarbearia):
                                lista_barbearias_proximas.append(barbearia)
                                lista_distancias_barbearia.append(distancia)
                    else:
                        print(f"Establishment is not a dictionary: {establishment}")
                        
    
    barbearias_e_distancias = [(barbearia_proximas, distancias_proximas) for barbearia_proximas, distancias_proximas in zip(lista_barbearias_proximas, lista_distancias_barbearia)]
    
    
    
    session['endereco_simplificado'] = endereco_simplificado
    return render_template('sistema-homepage.html', servicos=Servico.query.all(), lista_barbearias_proximas=barbearias_e_distancias, enderecoCliente=endereco_simplificado)

    
    
def normalize_address(address):
    # Normalizar o endereço para comparação (remover espaços, pontuação, etc.)
    import re
    return re.sub(r'\W+', '', address).lower()


@app.route('/perfil-barbearia/<nome_barbearia>/<distancia>')
def visitar_barbearia(nome_barbearia, distancia):
    barbearia = Barbearia.query.filter_by(nomeBarbearia = nome_barbearia).first()
    preco_servicos = PrecoServico.query.filter_by(idBarbearia = barbearia.idBarbearia).all()
    print(preco_servicos)
    servicos_dict = {}

    for servico in preco_servicos:
        nome_servico = Servico.query.filter_by(idServico=servico.idServico).first().nomeServico
        descricao_servico = Servico.query.filter_by(idServico=servico.idServico).first().descricao
        preco_servico = servico.PrecoServico
        data_inicio = servico.dataInicio
        duracao = servico.duracao
        
        servicos_dict[nome_servico] = {'preco_servico': preco_servico, 'duracao': duracao, 'descricao_servico': descricao_servico, 'id_servico': servico.idPrecoServico, 'data_inicio': data_inicio}

    # Agora, você pode iterar sobre os preços dos serviços e atualizar o dicionário
    for servico in preco_servicos:
        nome_servico = Servico.query.filter_by(idServico=servico.idServico).first().nomeServico
        descricao_servico = Servico.query.filter_by(idServico=servico.idServico).first().descricao
        preco_servico = servico.PrecoServico
        data_inicio = servico.dataInicio
        duracao = servico.duracao
        
        # Se o nome do serviço já existir no dicionário, atualize as informações
        if nome_servico in servicos_dict:
            servicos_dict[nome_servico] = {'preco_servico': preco_servico, 'duracao': duracao, 'descricao_servico': descricao_servico, 'id_servico': servico.idPrecoServico, 'data_inicio': data_inicio}

    # Agora, você pode iterar sobre o dicionário para obter as informações atualizadas
    lista_nomes_servico = []
    lista_valores_servico = []
    lista_duracao_servico = []
    lista_descricao = []
    lista_id_servico = []
    
    for nome_servico, info_servico in servicos_dict.items():
        lista_nomes_servico.append(nome_servico)
        lista_duracao_servico.append(info_servico['duracao'])
        lista_descricao.append(info_servico['descricao_servico'])
        lista_valores_servico.append(info_servico['preco_servico'])
        lista_id_servico.append(info_servico['id_servico'])

    return render_template('visitar-barbearia.html', barbearia = barbearia, distancia = distancia, inf_servicos = zip(lista_nomes_servico, lista_valores_servico, lista_duracao_servico, lista_id_servico, lista_descricao), servicos = Servico.query.all())

# ------------------------------------------------ Página de Serviço escolhido -----------------------------
# Define a rota '/servico/<nome_servico>' para a função 'servico_escolhido'
@app.route('/servico/<nome_servico>')
def servico_escolhido(nome_servico):    
    #Cria a variavel servico e da o valor do nome do servico escolhido pelo usuario.
    servico = Servico.query.filter_by(nomeServico=nome_servico).first()
    # Consulta a tabela 'PrecoServico' juntando com 'Servico' para filtrar pelo nome do serviço fornecido
    preco_servico = PrecoServico.query.join(Servico).filter(Servico.nomeServico == nome_servico).all()

    print('Acessando a pagina do serviço:', nome_servico)    

    if current_user.is_authenticated:
        endereco_simplificado = session.get('endereco_simplificado', None)
        usuario = Usuario.query.filter_by(idUsuario=current_user.idUsuario).first()
        
        if preco_servico:
            
            try:        
                # Inicializa listas para armazenar barbearias, valores dos serviços e IDs dos serviços
                valores_servicos = []
                id_servico = []
                duracao = []
                lista_barbearias = []
                lista_distancias = []
                
                # Itera sobre os registros de 'preco_servico' encontrados
                for preco in preco_servico:
                    
                    nome_barbearia = preco.idBarbearia
                    nome_barbearia = Barbearia.query.filter_by(idBarbearia = nome_barbearia).first()
                    nome_barbearia = nome_barbearia.nomeBarbearia

                    
                    duracao.append(preco.duracao) 
                    valores_servicos.append(preco.PrecoServico)  # Adiciona o valor do serviço à lista
                    id_servico.append(preco.idPrecoServico)  # Adiciona o ID do preço do serviço à lista

                    if preco:
                        id_barbearia = preco.idBarbearia  # Obtém o ID da barbearia associado ao preço do serviço
                        barbearias = Barbearia.query.filter_by(idBarbearia=id_barbearia).all()  # Consulta a barbearia pelo ID
                        
                        if endereco_simplificado:
                            print('Endereço Geolocalização:', endereco_simplificado)
                            
                            # Chama a função para obter as barbearias próximas
                            barbearias_e_distancias = obter_barbearia_e_distancia(barbearias, endereco_simplificado)
                            
                            if barbearias_e_distancias:
                                for barbearia_proxima, distancia in barbearias_e_distancias:
                                    lista_barbearias.append(barbearia_proxima)
                                    lista_distancias.append(distancia)
                                    
                                flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
                                flash(f'Obs: {servico.descricao}', 'descricao')
                                # Renderiza o template 'sistema-homepage.html' passando todos os serviços, as barbearias, os valores dos serviços e o nome do serviço
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), barbearias_valores_distancia=zip(lista_barbearias, lista_distancias, valores_servicos, id_servico, duracao), nome_servico=nome_servico, enderecoCliente = usuario.enderecoCliente, nome_barbearia = nome_barbearia)        
                                    
                            else:
                    
                                flash('Nenhuma barbearia encontrada para o serviço escolhido em sua região.', 'error')
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico, enderecoCliente = endereco_simplificado, nome_barbearia = nome_barbearia)
                        
                        else:
                            print('Endereço Geolocalização:', usuario.enderecoCliente)
                            
                            # Chama a função para obter as barbearias próximas
                            barbearias_e_distancias = obter_barbearia_e_distancia(barbearias, usuario.enderecoCliente)
                            
                            if barbearias_e_distancias:
                                for barbearia_proxima, distancia in barbearias_e_distancias:
                                    lista_barbearias.append(barbearia_proxima)
                                    lista_distancias.append(distancia)
                                    
                                    
                                flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
                                flash(f'Obs: {servico.descricao}', 'descricao')
                                # Renderiza o template 'sistema-homepage.html' passando todos os serviços, as barbearias, os valores dos serviços e o nome do serviço
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), barbearias_valores_distancia=zip(lista_barbearias, lista_distancias, valores_servicos, id_servico, duracao), nome_servico=nome_servico, enderecoCliente = usuario.enderecoCliente, nome_barbearia=nome_barbearia)    
                                    
                            else:
                                print('Nenhuma barbearia encontrada no raio de quilometragem.')
                                flash('Nenhuma barbearia encontrada para o serviço escolhido em sua região.', 'error')
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico, nome_barbearia=nome_barbearia)

                
            
            except Exception as e:
                print(e)
                
                nome_barbearia = preco.idBarbearia
                nome_barbearia = Barbearia.query.filter_by(idBarbearia = nome_barbearia).first()
                nome_barbearia = nome_barbearia.nomeBarbearia

                # Em caso de exceção, exibe uma mensagem de erro e redireciona para a página 'barber'
                flash('Nenhuma barbearia encontrada para o serviço escolhido em sua região.', 'error')
                return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico, nome_barbearia=nome_barbearia)
    
        else:
            flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
            flash(f'Obs: {servico.descricao}', 'descricao')
            flash('Nenhuma barbearia encontrada para o serviço escolhido em sua região.', 'error')
            return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico, nome_barbearia=nome_barbearia)   
        
    else:
        endereco_simplificado = session.get('endereco_simplificado', None)
            
        if preco_servico:
            try:        
                # Inicializa listas para armazenar barbearias, valores dos serviços e IDs dos serviços
                duracao = []
                id_servico = []
                valores_servicos = []
                lista_barbearias = []
                lista_distancias = []
                
                # Itera sobre os registros de 'preco_servico' encontrados
                for preco in preco_servico:
                    duracao.append(preco.duracao) 
                    valores_servicos.append(preco.PrecoServico)  # Adiciona o valor do serviço à lista
                    id_servico.append(preco.idPrecoServico)  # Adiciona o ID do preço do serviço à lista

                    if preco:
                        id_barbearia = preco.idBarbearia  # Obtém o ID da barbearia associado ao preço do serviço
                        barbearias = Barbearia.query.filter_by(idBarbearia=id_barbearia).all()  # Consulta a barbearia pelo ID
                        
                        if endereco_simplificado:
                            print('Endereço Geolocalização:', endereco_simplificado)
                            
                            # Chama a função para obter as barbearias próximas
                            barbearias_e_distancias = obter_barbearia_e_distancia(barbearias, endereco_simplificado)
                            
                            if barbearias_e_distancias:
                                for barbearia_proxima, distancia in barbearias_e_distancias:
                                    lista_barbearias.append(barbearia_proxima)
                                    lista_distancias.append(distancia)
                                    
                                flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
                                flash(f'Obs: {servico.descricao}', 'descricao')
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), barbearias_valores_distancia=zip(lista_barbearias, lista_distancias, valores_servicos, id_servico, duracao), nome_servico=nome_servico)
                                    
                            else:
                                print('Nenhuma barbearia encontrada no raio de quilometragem.')
                                flash('Nenhuma barbearia encontradada para o serviço escolhido em sua região.', 'error')
                                return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico)

                        else:
                            print('Nenhum endereço na geolocalização.')
                            endereco_simplificado = None
                            return render_template('sistema-homepage.html', servicos=Servico.query.all(), enderecoCliente = endereco_simplificado)    
                 
            except Exception as e:
                print(e)
                # Em caso de exceção, exibe uma mensagem de erro e redireciona para a página 'sistema-homepage'
                flash('Nenhum barbeiro encontrado para o serviço escolhido em sua região.', 'error')
                return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico)
    return render_template('sistema-homepage.html', servicos=Servico.query.all(), nome_servico=nome_servico)                    
            
# ------------------------------------------------ Página de agendamento -----------------------------------
# Esta rota renderiza uma página HTML para permitir que os usuários visualizem e reservem horários disponíveis para um serviço específico em uma determinada barbearia.
@app.route('/agendamentos/<nome_barbearia>/<id_servico>')
@login_required
def agendamento(nome_barbearia, id_servico):
    # Obter a data selecionada da solicitação
    data_selecionada = request.args.get('data')
    print(id_servico)
    # Obter informações do serviço com base no ID do serviço
    servico = PrecoServico.query.filter_by(idPrecoServico=id_servico).first()
    
    # Obter informações da barbearia com base no ID da barbearia associada ao serviço
    
    id_barbearia = servico.idBarbearia
    barbearia = Barbearia.query.filter_by(idBarbearia=id_barbearia).first()
    
    # Converter a duração do serviço para minutos
    duracao = converter_duracao_para_minutos(servico.duracao)
    
    # Calcular os horários disponíveis com base nas informações da barbearia e nos horários já agendados
    agendas = Agenda.query.filter_by(dataAtendimento=data_selecionada).all()
    
    horarios_agendados = [agenda.horarioAtendimento.strftime('%H:%M') for agenda in agendas]
    duracoes_agendadas = [converter_duracao_para_minutos(PrecoServico.query.filter_by(idPrecoServico=agenda.idPrecoServico).first().duracao) for agenda in agendas]
    horarios_disponiveis = calcular_horarios_disponiveis(barbearia.horaInicio, barbearia.horaFim, duracao, horarios_agendados, duracoes_agendadas)
    horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
    
    # Filtrar os horários disponíveis para garantir que apenas os horários disponíveis sejam exibidos na página HTML
    horarios_disponiveis = [horario for horario in horarios_disponiveis if horario not in horarios_indisponiveis]

    # Renderizar a página HTML com os horários disponíveis
    return render_template('reservar-horario.html', id_servico=id_servico, horarios=horarios_disponiveis)


# Esta rota é uma rota de API que retorna os horários disponíveis em formato JSON para um serviço específico em uma determinada barbearia.
@app.route('/agendamentos/horarios-disponiveis', methods=['GET'])
@login_required
def horarios_disponiveis_js():
    # Obter a data selecionada da solicitação
    data_selecionada = request.args.get('data')
    
    # Obter o ID do serviço da solicitação
    id_servico = request.args.get('id_servico')
    
    # Obter informações do serviço com base no ID do serviço
    servico = PrecoServico.query.filter_by(idPrecoServico=id_servico).first()
    
    # Obter informações da barbearia com base no ID da barbearia associada ao serviço
    id_barbearia = servico.idBarbearia
    barbearia = Barbearia.query.filter_by(idBarbearia=id_barbearia).first()
    
    # Converter a duração do serviço para minutos
    duracao = converter_duracao_para_minutos(servico.duracao)
    
    # Calcular os horários agendados e suas durações
    agendas = Agenda.query.filter_by(dataAtendimento=data_selecionada).all()

    duracoes_agendadas = []
    horarios_agendados = []
    
    # Inicializa um dicionário para contar quantos agendamentos existem para cada horário
    horario_count = {}
    
    # Itera sobre todas as agendas obtidas para a data selecionada
    for agenda in agendas: 
        # Verifica se o status do agendamento é igual a 1 (ativo/não cancelado)
        if agenda.idStatus == 1:
            # Formata o horário do agendamento como uma string no formato 'HH:MM'
            horario = agenda.horarioAtendimento.strftime('%H:%M')
            
            # Se o horário ainda não está no dicionário 'horario_count', inicializa com 0
            if horario not in horario_count:
                horario_count[horario] = 0
            
            # Incrementa a contagem de agendamentos para o horário atual
            horario_count[horario] += 1
            
            # Se o número de agendamentos para o horário atual for igual ao número de barbeiros disponíveis
            if horario_count[horario] == int(barbearia.qtdBarbeiros):
                # Adiciona o horário à lista de horários agendados
                horarios_agendados.append(horario)
                
                # Converte a duração do serviço agendado para minutos
                duracao_agendada = converter_duracao_para_minutos(PrecoServico.query.filter_by(idPrecoServico=agenda.idPrecoServico).first().duracao)
                
                # Adiciona a duração do serviço agendado à lista de durações agendadas
                duracoes_agendadas.append(duracao_agendada)

    # Calcular os horários disponíveis com base nas informações da barbearia e nos horários já agendados
    horarios_disponiveis = calcular_horarios_disponiveis(barbearia.horaInicio, barbearia.horaFim, duracao, horarios_agendados, duracoes_agendadas)

    # Retornar os horários disponíveis em formato JSON
    return jsonify(horarios_disponiveis)

# Define a rota '/coletar-agendamento/<int:id_servico>' para a função 'coletar_agendamento' usando o método POST
@app.route('/coletar-agendamento/<int:id_servico>', methods=['POST'])
def coletar_agendamento(id_servico):
    print('id servico:',id_servico)
    # Coleta os dados do formulário enviados via método POST
    dataAgendamento = request.form['dataAgendamento']  # Data do agendamento
    horaAgendamento = request.form['horaAgendamento']  # Hora do agendamento
    
    # Obtém a data atual
    data_atual = datetime.now().date()
    hora_atual = datetime.now().replace(microsecond=0).time()  # Ajusta a hora atual para remover os microssegundos
    
    # Converte a data do agendamento de string para datetime
    dataAgendamento_datetime = datetime.strptime(dataAgendamento, '%Y-%m-%d').date()
    # Converte a hora do agendamento de string para datetime
    horaAgendamento_datetime = datetime.strptime(horaAgendamento, '%H:%M').time()
    
    print(horaAgendamento_datetime, hora_atual)
    print(dataAgendamento_datetime, data_atual)
    
    # Verifica se a data e hora do agendamento são válidas
    if dataAgendamento_datetime < data_atual:
        flash('Escolha uma data válida.', 'error')
        return redirect(url_for('agendamento', nome_barbearia = PrecoServico.query.filter_by(idPrecoServico = id_servico).first().idBarbearia, id_servico = id_servico))


    elif dataAgendamento_datetime == data_atual and hora_atual > horaAgendamento_datetime:
        flash('Escolha um horário válido.', 'error')
        return redirect(url_for('agendamento', nome_barbearia = PrecoServico.query.filter_by(idPrecoServico = id_servico).first().idBarbearia, id_servico = id_servico))
        
    # Cria uma nova instância de 'Agenda' com os dados coletados e o ID do serviço fornecido
    nova_agenda = Agenda(idPrecoServico=id_servico, idUsuario=current_user.idUsuario, idStatus=1, dataAtendimento=dataAgendamento, horarioAtendimento=horaAgendamento)
    
    # Adiciona o novo agendamento à sessão do banco de dados e confirma a transação
    db.session.add(nova_agenda)
    db.session.commit()
    
    # Converte a data do agendamento de string para datetime
    dataAgendamento_datetime = datetime.strptime(dataAgendamento, '%Y-%m-%d')
    # Formata a data para o formato brasileiro (dd/mm/yyyy)
    dataAgendamento_br = dataAgendamento_datetime.strftime('%d/%m/%Y')
    
    # Exibe uma mensagem de sucesso com os detalhes do agendamento
    flash(f"Agendamento Concluido! Foi feito uma reserva na data: {dataAgendamento_br}, ás: {horaAgendamento}.", 'success')
    
    # Redireciona o usuário para a página 'reservasCliente'
    return redirect(url_for('reservasCliente'))


# ------------------------------------------------ Página de reservas do cliente ----------------------------
# Define a rota '/reservas' para a função 'reservasCliente' e exige que o usuário esteja autenticado para acessar
@app.route('/reservas')
@login_required
def reservasCliente():
    # Verifica se o usuário atual está autenticado
    if current_user.is_authenticated:
        id_usuario = current_user.idUsuario  # Obtém o ID do usuário atual

        # Consulta a tabela 'Agenda' para obter todas as reservas feitas pelo usuário atual
        agendas = Agenda.query.filter_by(idUsuario=id_usuario).all()
        
        # Obtém a data atual e a hora atual
        data_atual = datetime.now().date()
        hora_atual = datetime.now()
        hora_atual = hora_atual.replace(microsecond=0)
        
        # Função de chave para ordenar por data e hora
        def ordenar_agenda(agenda):
            # Transforma a hora da agenda em uma data e hora completa para comparação
            hora_agenda = datetime.combine(data_atual, agenda.horarioAtendimento)
            
            # Retorna uma tupla com a data e a hora da agenda
            return (agenda.dataAtendimento, hora_agenda)
        
        # Ordena a lista de reservas usando a função de chave personalizada
        agendas_ordenadas = sorted(agendas, key=ordenar_agenda)
        agendas_ordenadas.reverse()
        
        # Itera sobre as agendas para verificar e atualizar o status
        for agenda in agendas_ordenadas:
            if agenda.idStatus == 1:
                if agenda.dataAtendimento <= data_atual:
                    data_hora_str = f'{agenda.dataAtendimento} {agenda.horarioAtendimento}'
                    data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M:%S')
                    
                    print(type(data_hora))
                    print(type(hora_atual))
                    if hora_atual >= data_hora:
                        # Se a data for hoje e o horário for anterior ao horário atual,
                        # muda o idStatus para 3 (indicando que a reserva está vencida)
                        agenda.idStatus = 3
                    
        # Confirma as alterações no banco de dados
        db.session.commit()
        
    # Renderiza o template 'reservas-clientes.html', passando a lista de reservas futuras
    return render_template('reservas-clientes.html', agendas=agendas_ordenadas, servicos=Servico.query.all())

#Essa rota Cancela o agendamento caso o cliente peça.
@app.route('/cancelar-agendamento/<int:idReserva>')
def cancelarAgendamento(idReserva):
    print(idReserva)
    agenda = Agenda.query.get_or_404(idReserva)  # Recupera o objeto Agenda pelo id_agenda
    
    if agenda.idStatus == 3:
        flash('Impossível cancelar um agendamento concluido.', 'error')
        return redirect(url_for('reservasCliente'))
    
    elif agenda.idStatus == 1:
        agenda.idStatus = 2  # Atualiza o status do agendamento para cancelado
        db.session.commit()
        return redirect(url_for('reservasCliente'))
    
    else:
        flash('Ocorreu um erro ao cancelar. Entre em contato com a barbearia','error')
        return redirect(url_for('reservasCliente'))

# ------------------------------------------------ Página de agendamentos do barbeiro ------------------------
# Define a rota '/agendamentos' para a função 'reservasBarbeiro' e exige que o usuário esteja autenticado para acessar
@app.route('/agendamentos')
@login_required
def reservasBarbeiro():
    # Obtém o ID do usuário logado
    id_usuario_logado = current_user.idUsuario
    print('id do usuario é:', id_usuario_logado)
    
    # Verifica se o usuário é barbeiro
    if current_user.barbeiro == '1':
        id_barbearia_usuario = current_user.idBarbearia_fk  # Obtém o ID da barbearia associada ao usuário
        nome_barbearia = Barbearia.query.filter_by(idBarbearia=id_barbearia_usuario).first()
        nome_barbearia = nome_barbearia.nomeBarbearia

        # Consulta para verificar as agendas do barbeiro associadas à barbearia
        agenda_usuario = (Agenda.query
                        .join(PrecoServico, Agenda.idPrecoServico == PrecoServico.idPrecoServico)
                        .filter(PrecoServico.idBarbearia == id_barbearia_usuario)
                        .all())

        # Se houver agendas, cria uma lista com essas agendas
        if agenda_usuario:
            # Função de chave para ordenar as agendas
            def ordenar_agenda(agenda):
                return agenda.dataAtendimento, agenda.horarioAtendimento

            # Ordena a lista de agendas usando a função de chave personalizada
            agendas_ordenadas = sorted(agenda_usuario, key=ordenar_agenda)
            agendas_ordenadas.reverse()
            
            # Renderiza o template 'reservas-barbeiro.html', passando a lista de agendas ordenadas
            return render_template('reservas-barbeiro.html', agendas=agendas_ordenadas, nome_barbearia=nome_barbearia, servicos=Servico.query.all())
        else:
            # Se não houver agendas, renderiza o template com uma lista vazia
            return render_template('reservas-barbeiro.html', agendas=[], nome_barbearia=nome_barbearia, servicos=Servico.query.all())
        
    else:
        flash("Acesso negado. Você não é um barbeiro.",'error')
        # Redireciona o usuário para a página 'barber' se ele não for barbeiro
        return redirect(url_for('barber'))


# ---------------------------------------- Página de cadastrar serviço do barbeiro ----------------------------

@app.route('/cadastro-servico')
def cadastrarServicos():
    usuario = Usuario.query.filter_by(idUsuario = current_user.idUsuario).first()
    barbearia = Barbearia.query.filter_by(idBarbearia = usuario.idBarbearia_fk).first()
    return render_template('cadastrar_servico.html', servicos = Servico.query.all(), nome_barbearia = barbearia.nomeBarbearia)
    

# Define a função que coleta os serviços do barbeiro e salva no banco
@app.route('/coletar-servicos-barbeiro', methods=['POST'])
def coletarServicosBarbeiro():
    # Obter todos os checkboxes marcados
    servicos_selecionados = request.form.getlist('servico_valor')
    
    servico_valor_pairs = []  # Inicializa uma lista para armazenar pares de serviço e valor

    if not servicos_selecionados:
        flash('Selecione ao menos algum serviço, o valor e a duração.', 'error')
        
    # Processar os dados do formulário
    for servico_id in servicos_selecionados:
        # Obter o valor do input associado a este serviço
        valor_key = f'valorServico_{servico_id}'
        duracao_key = f'duracao_{servico_id}'
        valor = request.form.get(valor_key, '')
        duracao = request.form.get(duracao_key, '')
        
        
        if valor and duracao:  # Certifique-se de que há um valor associado
            # Cria uma nova instância de 'PrecoServico' com os dados coletados
            preco_servico_barbeiro = PrecoServico(dataInicio=datetime.now().strftime('%Y-%m-%d'), 
                                                  idBarbearia=current_user.idBarbearia_fk, 
                                                  idServico=servico_id, 
                                                  PrecoServico=valor,
                                                  duracao = duracao)
            
            # Adiciona o novo preço de serviço à sessão do banco de dados e confirma a transação
            db.session.add(preco_servico_barbeiro)
            db.session.commit()
            
        else:
            # Se algum serviço não tiver valor, exibe uma mensagem de erro e redireciona
            flash('Coloque valor e a duração em todos os serviços selecionados.', 'error')
            return redirect(url_for('cadastrarServicos'))
    if valor:
        flash('Serviços cadastrados com sucesso!', 'success') 
       
    # Printar os serviços e valores (não necessário para a funcionalidade, mas útil para depuração)
    for servico, valor in servico_valor_pairs:
        print(f'Serviço: {servico}, Valor: {valor}')

    # Redireciona o usuário para a página 'cadastrarServicos' após concluir o processamento
    return redirect(url_for('cadastrarServicos'))


# ---------------------------------------- Página de perfil para barbearia ----------------------------

@app.route('/meu-perfil-barbearia/<nome_barbearia>')
def perfil_barbearia(nome_barbearia):
    barbearia = Barbearia.query.filter_by(nomeBarbearia = nome_barbearia).first()
    usuario = Usuario.query.filter_by(idBarbearia_fk = barbearia.idBarbearia).first()
    preco_servicos = PrecoServico.query.filter_by(idBarbearia = barbearia.idBarbearia).all()
    
    servicos_dict = {}

    for servico in preco_servicos:
        nome_servico = Servico.query.filter_by(idServico=servico.idServico).first().nomeServico
        preco_servico = servico.PrecoServico
        data_inicio = servico.dataInicio
        
        servicos_dict[nome_servico] = {'preco_servico': preco_servico, 'data_inicio': data_inicio}

    # Agora, você pode iterar sobre os preços dos serviços e atualizar o dicionário
    for servico in preco_servicos:
        nome_servico = Servico.query.filter_by(idServico=servico.idServico).first().nomeServico
        preco_servico = servico.PrecoServico
        data_inicio = servico.dataInicio
        
        # Se o nome do serviço já existir no dicionário, atualize as informações
        if nome_servico in servicos_dict:
            servicos_dict[nome_servico] = {'preco_servico': preco_servico, 'data_inicio': data_inicio}

    # Agora, você pode iterar sobre o dicionário para obter as informações atualizadas
    lista_nomes_servico = []
    lista_valores_servico = []

    for nome_servico, info_servico in servicos_dict.items():
        lista_nomes_servico.append(nome_servico)
        lista_valores_servico.append(info_servico['preco_servico'])

        print(nome_servico, info_servico['preco_servico'], info_servico['data_inicio'])
    
    return render_template('perfil_barbearia.html', servicos = Servico.query.all(), barbearia = barbearia, usuario = usuario, servico = zip(lista_nomes_servico,lista_valores_servico), nome_barbearia = barbearia.nomeBarbearia)


@app.route('/coletar-alt-barbearia', methods=['POST'])
def coletar_alt_barbearia():
    
    novoNome = request.form['novoNome']
    novoTelefone = request.form['novoTelefone']
    novoEmail = request.form['novoEmail']
    novoEndereco = request.form['novoEndereco']
    novaQtdBarbeiros = request.form['novaQtdBarbeiros']
    novaHoraInicio = request.form['novaHoraInicio']
    novaHoraFinal = request.form['novaHoraFinal']
    id_barbearia = request.form['idBarbearia']
    action = request.form.get('action')
    
    barbearia = Barbearia.query.filter_by(idBarbearia = id_barbearia).first()
    
    switch = request.form.get('switch', barbearia.disponibilidade)
    
    if switch == 'on':
        status = 'ativo'
    else:
        status='inativo'
    
    print(status)
    
    
    if action == 'Salvar':
        if barbearia:
            print('Entrei aqui')
            # Atualiza os atributos da barbearia com as novas informações
            barbearia.nomeBarbearia = novoNome
            barbearia.telefone = novoTelefone
            barbearia.email = novoEmail
            barbearia.enderecoBarbearia = novoEndereco
            barbearia.qtdBarbeiros = novaQtdBarbeiros
            barbearia.horaInicio = novaHoraInicio
            barbearia.horaFim = novaHoraFinal
            barbearia.disponibilidade = status
            # Salva as alterações no banco de dados
            db.session.commit()
            
            flash('Perfil atualizado.', 'success')
            return redirect(url_for('perfil_barbearia', nome_barbearia=barbearia.nomeBarbearia))
    
    else:
        return redirect(url_for('perfil_barbearia', nome_barbearia=barbearia.nomeBarbearia))


# ---------------------------------------- Página de perfil para clientes ----------------------------
@app.route('/meu-perfil/<nome_cliente>')
def perfil_usuario(nome_cliente):
    id_usuario = current_user.idUsuario
    usuario = Usuario.query.filter_by( idUsuario = id_usuario).first()
    
    endereco = usuario.enderecoCliente
    # Dividir o endereço em partes com base nas vírgulas
    partes_endereco = endereco.split(',')

    # Limpar os espaços em branco ao redor de cada parte
    partes_endereco = [parte.strip() for parte in partes_endereco]
    
    # Extrair as variáveis individuais
    rua = partes_endereco[0]
    bairro = partes_endereco[1]
    numero = partes_endereco[2]
    cidade = partes_endereco[3]
    estado = partes_endereco[4]

    return render_template('perfil_usuario.html', servicos = Servico.query.all(), usuario = usuario, rua = rua, numero = numero, bairro=bairro, cidade=cidade, estado = estado)


@app.route('/coletar-alt-usuario', methods=['POST'])
def coletar_alt_usuario():
    novoNome = request.form['alterarNome']
    novoTelefone = request.form['alterarTelefone']
    novoEmail = request.form['alterarEmail']
    novaRua = request.form['novaRua']
    novoNumero= request.form['novoNumero']
    novoBairro= request.form['novoBairro']
    novoCidade= request.form['novaCidade']
    novoEstado = request.form['novoEstado']
    action = request.form['action']
    
    
    novoEndereco = f'{novaRua}, {novoNumero}, {novoBairro}, {novoCidade}, {novoEstado}'
    print(novoEndereco)
    
    if action == "Salvar":
        usuario = Usuario.query.filter_by(idUsuario = current_user.idUsuario).first()
        
        usuario.nomeUsuario = novoNome
        usuario.telefone = novoTelefone
        usuario.email = novoEmail
        usuario.enderecoCliente = novoEndereco
        
        db.session.commit()
            
        flash('Perfil atualizado.', 'success')
    
    return redirect(url_for('perfil_usuario', nome_cliente = current_user.nomeUsuario))
    
    
#------------------------- Sair -----------------------
#Rota que oficioaliza o logout do usuario.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if "__main__" == __name__:
    app.run(debug = True)