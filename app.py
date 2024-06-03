from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from model import db, Usuario, Agenda, Barbearia, PrecoServico, Servico, init_db
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from scripts.scripts import calcular_horarios_disponiveis, calcular_horarios_indisponiveis, converter_duracao_para_minutos, enviar_email_recuperar_senha
import random as rd
from datetime import datetime


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
    email = request.form['email']
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
    if not all([nomeUsuario, telefoneCliente, email, cpf]):
        flash('Houve algum campo em branco.', 'error')
        return redirect(url_for('cadastrar'))
    
    elif temBarbearia == 'sim' and not all([nomeBarbearia, telefoneBarbearia, qtdBarbeiros, rua, numeroEndereco, bairro, cep, cidade, estado, senha_barbearia1, senha_barbearia2, horaInicio, horaFim]):
        flash('Houve algum campo em branco', 'error')
        return redirect(url_for('cadastrar'))
        
    elif temBarbearia == 'sim' and qtdBarbeiros == '0':
        flash('Quantidade de barbeiros inválida.', 'error')
        return redirect(url_for('cadastrar'))

    # Verifica se as senhas fornecidas coincidem e cria o usuario.
    if str(senha_barbearia1) == str(senha_barbearia2) or str(senha_cliente1) == str(senha_cliente2):
        
        # Formata os dados antes de criar um novo usuário.
        nomeUsuario = nomeUsuario.capitalize()
        email = email.lower()

        # Cria um novo objeto de usuário com os dados fornecidos.
        if senha_cliente1:
            novo_usuario = Usuario(cpf=cpf, nomeUsuario=nomeUsuario, email=email, telefone=telefoneCliente, senha=senha_cliente1, barbeiro = False, idBarbearia_fk = None)
        else:
            novo_usuario = Usuario(cpf=cpf, nomeUsuario=nomeUsuario, email=email, telefone=telefoneCliente, senha=senha_barbearia1, barbeiro = False, idBarbearia_fk = None)
       
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

        # Se o usuario for uma barbearia, vamos criar sua barbearia.
        if temBarbearia == 'sim':
            
            # Constrói o endereço completo
            endereco = f'{rua}, {numeroEndereco} - {bairro}, CEP: {cep} - {cidade}, {estado}'
            
            # Cria uma nova instância de 'Barbearia' com os dados coletados
            novoBarbeiro = Barbearia(nomeBarbearia=nomeBarbearia, telefone=telefoneBarbearia, endereco=endereco, qtdBarbeiros = qtdBarbeiros, horaInicio=horaInicio, horaFim=horaFim)
            
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
        barbeiro = int(current_user.barbeiro)
        print(barbeiro, type(barbeiro))  # Imprime o valor e o tipo de 'barbeiro' para depuração
        # Renderiza o template 'sistema-homepage.html', passando o valor de 'barbeiro' e a lista de todos os serviços
        return render_template('sistema-homepage.html', barbeiro=barbeiro, servicos=Servico.query.all())
    else:
        # Renderiza o template 'sistema-homepage.html', passando apenas a lista de todos os serviços
        return render_template('sistema-homepage.html', servicos=Servico.query.all())


# ------------------------------------------------ Página de Serviço escolhido -----------------------------
# Define a rota '/servico/<nome_servico>' para a função 'servico_escolhido'
@app.route('/servico/<nome_servico>')
def servico_escolhido(nome_servico):    
    # Consulta a tabela 'PrecoServico' juntando com 'Servico' para filtrar pelo nome do serviço fornecido
    preco_servico = PrecoServico.query.join(Servico).filter(Servico.nomeServico == nome_servico).all()
    #Cria a variavel servico e da o valor do nome do servico escolhido pelo usuario.
    servico = Servico.query.filter_by(nomeServico=nome_servico).first()
    
    if preco_servico:
        try:
            # Inicializa listas para armazenar barbearias, valores dos serviços e IDs dos serviços
            barbearias = []
            valores_servicos = []
            id_servico = []
            
            # Itera sobre os registros de 'preco_servico' encontrados
            for preco in preco_servico:
                if preco:
                    id_barbearia = preco.idBarbearia  # Obtém o ID da barbearia associado ao preço do serviço
                    barbearia = Barbearia.query.filter_by(idBarbearia=id_barbearia).first()  # Consulta a barbearia pelo ID
                    
                    if barbearia:
                        barbearias.append(barbearia)  # Adiciona a barbearia à lista
                        valores_servicos.append(preco.PrecoServico)  # Adiciona o valor do serviço à lista
                        id_servico.append(preco.idPrecoServico)  # Adiciona o ID do preço do serviço à lista
            
            flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
            flash(f'Obs: {servico.descricao}', 'descricao')
            
            # Renderiza o template 'sistema-homepage.html' passando todos os serviços, as barbearias, os valores dos serviços e o nome do serviço
            return render_template('sistema-homepage.html', servicos=Servico.query.all(), barbearias_valores=zip(barbearias, valores_servicos, id_servico), nome_servico=nome_servico)
        
        except:
            # Em caso de exceção, exibe uma mensagem de erro e redireciona para a página 'barber'
            flash('Nenhum barbeiro encontrado para o serviço escolhido.', 'error')
            return redirect(url_for('barber'))
    else:
        flash(f'Você selecionou o serviço: {nome_servico}.', 'servico')
        flash(f'Obs: {servico.descricao}', 'descricao')
        flash('Nenhum barbeiro encontrado para o serviço escolhido.', 'error')
        return redirect(url_for('barber'))


# ------------------------------------------------ Página de agendamento -----------------------------------
# Esta rota renderiza uma página HTML para permitir que os usuários visualizem e reservem horários disponíveis para um serviço específico em uma determinada barbearia.
@app.route('/agendamentos/<nome_barbearia>/<id_servico>')
@login_required
def agendamento(nome_barbearia, id_servico):
    # Obter a data selecionada da solicitação
    data_selecionada = request.args.get('data')
    
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
    
    #Verifica se o status do agendamento não é cancelado.
    for agenda in agendas:
        if agenda.idStatus == 1:
            horarios_agendados = [agenda.horarioAtendimento.strftime('%H:%M')]
            duracoes_agendadas = [converter_duracao_para_minutos(PrecoServico.query.filter_by(idPrecoServico=agenda.idPrecoServico).first().duracao)]
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
        
        lista_de_reservas = []  # Inicializa uma lista para armazenar as reservas futuras
        data_atual = datetime.now().date()  # Obtém a data atual
    
        # Itera sobre as reservas do usuário
        for agenda in agendas:
            # Verifica se a data do atendimento é igual ou posterior à data atual
            if agenda.dataAtendimento >= data_atual:
                lista_de_reservas.append(agenda)  # Adiciona a reserva à lista de reservas futuras

        # Ordena a lista de reservas pelo campo 'dataAtendimento', do mais próximo ao mais distante
        lista_de_reservas = sorted(lista_de_reservas, key=lambda x: x.dataAtendimento)

    # Renderiza o template 'reservas-clientes.html', passando a lista de reservas futuras
    return render_template('reservas-clientes.html', agendas=lista_de_reservas, servicos=Servico.query.all())

#Essa rota Cancela o agendamento caso o cliente peça.
@app.route('/cancelar-agendamento/<int:idReserva>')
def cancelarAgendamento(idReserva):
    print(idReserva)
    agenda = Agenda.query.get_or_404(idReserva)  # Recupera o objeto Agenda pelo id_agenda
    agenda.idStatus = 2  # Atualiza o status do agendamento para cancelado
    db.session.commit()
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

        # Consulta para verificar as agendas do barbeiro associadas à barbearia
        agenda_usuario = (Agenda.query
                          .join(PrecoServico, Agenda.idPrecoServico == PrecoServico.idPrecoServico)
                          .filter(PrecoServico.idBarbearia == id_barbearia_usuario)
                          .all())

        # Se houver agendas, cria uma lista com essas agendas
        if agenda_usuario:
            lista_agendas = []
            for agenda in agenda_usuario:
                lista_agendas.append(agenda)
            
            # Renderiza o template 'reservas-barbeiro.html', passando a lista de agendas
            return render_template('reservas-barbeiro.html', agendas=lista_agendas)
        else:
            # Se não houver agendas, renderiza o template com uma lista vazia
            return render_template('reservas-barbeiro.html', agendas=[])
    else:
        flash("Acesso negado. Você não é um barbeiro.",'error')
        # Redireciona o usuário para a página 'barber' se ele não for barbeiro
        return redirect(url_for('barber'))


# ---------------------------------------- Página de cadastrar serviço do barbeiro ----------------------------

@app.route('/cadastro-servico')
def cadastrarServicos():
    return render_template('cadastrar_servico.html', servicos = Servico.query.all())
    

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
            flash('Serviços cadastrados com sucesso!', 'success')
        else:
            # Se algum serviço não tiver valor, exibe uma mensagem de erro e redireciona
            flash('Coloque valor e a duração em todos os serviços selecionados.', 'error')
            return redirect(url_for('cadastrarServicos'))
        
    # Printar os serviços e valores (não necessário para a funcionalidade, mas útil para depuração)
    for servico, valor in servico_valor_pairs:
        print(f'Serviço: {servico}, Valor: {valor}')

    # Redireciona o usuário para a página 'cadastrarServicos' após concluir o processamento
    return redirect(url_for('cadastrarServicos'))


#------------------------- Sair -----------------------
#Rota que oficioaliza o logout do usuario.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if "__main__" == __name__:
    app.run(debug = True, host= '192.168.0.113')