from flask import Flask, render_template, flash, redirect, url_for, request
from model import db, Usuario, Agenda, Barbearia, PrecoServico, Servico
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from scripts.enviar_email_recuperar import enviar_email_recuperar_senha
import random as rd
from datetime import datetime


app = Flask(__name__)


app.config['SECRET_KEY'] = 'A123S456D789'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/bdnaregua'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app) 
login_manager.login_view = 'login' #Rota de login
login_manager.login_message='Faça Login Ou Cadastre-se Para Acessar' #Mensagem que aparecerá caso você seja obrigado a fazer o login
login_manager.login_message_category='error'#Categoria do login    
    


@login_manager.user_loader
def load_user(user_id):
    user = Usuario.query.filter_by(cpf=user_id).first()
    return user


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
                print(f'O cliente do email: {login} entrou')
                print(usuario_email)
                return redirect(url_for('barber'))
        else:
            # Se a senha estiver incorreta, exibe uma mensagem de erro e redireciona para a página de login.
            flash('Usuário ou senha incorreta', 'error')
            return redirect(url_for('login'))
    else:
        # Se o usuário não existir, exibe uma mensagem de erro e redireciona para a página de login.
        flash('Usuário incorreto', 'error')
        return redirect(url_for('login'))


@app.route('/cadastrar')
def cadastrar():
    #Rota cadastrar, apenas renderiza o template cadastrar.html
    return render_template('cadastrar.html')

# Esta função é uma rota Flask que recebe os dados de cadastro para cadastrar um CLIENTE 
@app.route('/coletar-cadastro', methods=['POST'])
def coletar_cadastro():
    # Obtém os dados do formulário enviado.
    nomeUsuario = request.form['nomeCompleto']
    cpf = request.form['cpf']
    telefone = request.form['telefone']
    email = request.form['email']
    senha1 = request.form['senha1']
    senha2 = request.form['senha2']

    # Verifica se algum campo obrigatório está em branco.
    if (nomeUsuario == '') or (telefone == '') or (email == '') or (senha1 == '') or (senha2 == ''):
        print('Houve algum campo em branco.')
        # Redireciona de volta para a página de cadastro.
        return redirect(url_for('cadastrar'))
    else:
        # Verifica se as senhas fornecidas coincidem.
        if str(senha1) == str(senha2):
            # Formata os dados antes de criar um novo usuário.
            nomeUsuario = nomeUsuario.capitalize()
            email = email.lower()

            # Cria um novo objeto de usuário com os dados fornecidos.
            novo_usuario = Usuario(cpf=cpf, nomeUsuario=nomeUsuario, email=email, telefone=telefone, senha=senha1, barbeiro = False)
            
            # Adiciona o novo usuário ao banco de dados.
            db.session.add(novo_usuario)
            db.session.commit()
            print('Parabéns!! Novo cliente cadastrado no banco de dados!\n')
            # Redireciona para a página inicial após o cadastro bem-sucedido.
            return redirect(url_for('login'))
        else:
            print('As senhas não coincidem')
            # Redireciona de volta para a página de cadastro.
            return redirect(url_for('cadastrar'))


@app.route('/cadastrar-barbeiro')
def cadastrar_barbeiro():
    print('Entrei aqui')
    return render_template('cadastro-barbeiro.html')

# Esta função é uma rota Flask que recebe os dados de cadastro do barbeiro de um formulário HTML via método POST.
@app.route('/coletar-cadastro-barbeiro', methods=['POST'])
def coletar_cadastro_barbeiro():
    # Verifica se o usuário atual está autenticado
    if current_user.is_authenticated:
        id_usuario = current_user.idUsuario  # Obtém o ID do usuário atual
        print('O id do user é:', id_usuario)
    
    # Coleta os dados do formulário enviados via método POST
    nomeBarbearia = request.form['nomeBarbearia']  # Nome da barbearia
    telefone = request.form['telefone']  # Telefone da barbearia
    rua = request.form['rua']  # Rua do endereço da barbearia
    numero = request.form['numero']  # Número do endereço da barbearia
    bairro = request.form['bairro']  # Bairro do endereço da barbearia
    cep = request.form['cep']  # CEP do endereço da barbearia
    cidade = request.form['cidade']  # Cidade do endereço da barbearia
    estado = request.form['estado']  # Estado do endereço da barbearia
    horaInicio = request.form['horario_abertura_sim']  # Horário de abertura da barbearia
    horaFim = request.form['horario_fechamento_sim']  # Horário de fechamento da barbearia
    barbeiro = True  # Define que o usuário é barbeiro
    
    # Constrói o endereço completo
    endereco = f'{rua}, {numero} - {bairro}, CEP: {cep} - {cidade}, {estado}'
    
    # Cria uma nova instância de 'Barbearia' com os dados coletados
    novoBarbeiro = Barbearia(nomeBarbearia=nomeBarbearia, telefone=telefone, endereco=endereco, horaInicio=horaInicio, horaFim=horaFim)
    
    # Adiciona a nova barbearia à sessão do banco de dados e confirma a transação
    db.session.add(novoBarbeiro)
    db.session.commit()

    # Obter o idBarbearia da barbearia recém-criada
    id_barbearia = novoBarbeiro.idBarbearia

    # Consulta o banco de dados para encontrar o usuário pelo seu ID
    usuario = Usuario.query.filter_by(idUsuario=id_usuario).first()
    
    if usuario:
        # Atualiza o usuário para indicar que ele é barbeiro e associa a barbearia recém-criada
        usuario.barbeiro = True
        usuario.idBarbearia_fk = id_barbearia
        db.session.commit()  # Confirma a transação para salvar as alterações

    # Redireciona o usuário para a página 'barber'
    return redirect(url_for('barber'))
    

@app.route('/esq-senha')
def esq_senha():
    return render_template('esqueci_minha_senha.html')

# Esta função é uma rota Flask que recebe os dados de esqueci minha senha.
@app.route('/coletar_email_recuperar', methods=['POST'])
def coletar_email_recuperar():
     
    global email
    email = request.form['email']
    
    global codigo
    codigo = rd.randint(100000, 999999)
    
    global dicionario_mudar_senha
    dicionario_mudar_senha = {f'{email}':f'{codigo}'}
    
    usuario_email = Usuario.query.filter_by(email=email).first()
    
    if usuario_email:
        
        global codCliente
        codCliente = rd.randint(1000, 9999)
        
        enviar_email_recuperar_senha(email, codigo)
        return redirect(url_for('token_acess', codCliente = codCliente))
    
    else:
        flash('Usuario não cadastrado.', 'error')
        return redirect(url_for('esq_senha'))
        

@app.route('/token/<codCliente>')
def token_acess(codCliente):
    print(dicionario_mudar_senha.values())
    return render_template('token_de_acesso.html')


@app.route('/coletar_token', methods=['POST'])
def coletar_token():
    print(email)
    token1 = request.form['token1']
    token2 = request.form['token2']
    token3 = request.form['token3']
    token4 = request.form['token4']
    token5 = request.form['token5']
    token6 = request.form['token6']
    
    token = f'{token1}{token2}{token3}{token4}{token5}{token6}'

    if token in dicionario_mudar_senha.values():
        print('Token Autorizado.')
        return redirect(url_for('criar_senha'))
    else:

        flash('Codigo incorreto.', 'error')
        return redirect(url_for('token_acess', codCliente=codCliente))


@app.route('/criar-senha')
def criar_senha():
    return render_template('criar_senha_nova.html')


@app.route('/coletar_nova_senha', methods=['POST'])
def coletar_nova_senha():
    
    print(email)
    senha = request.form['senha']
    confirmarSenha = request.form['confirmarSenha']

    if senha == confirmarSenha:
        usuario = Usuario.query.filter_by(email=email).first()    
            
        usuario.senha = senha

        db.session.commit()
        
        sucess = "Senha alterada com sucesso!"
        flash(sucess, 'success')
        return redirect(url_for('login'))
    else:
        
        flash('As senhas não coincidem. Tente novamente.','error')
        return redirect(url_for('criar_senha'))


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


# Define a rota '/servico/<nome_servico>' para a função 'servico_escolhido'
@app.route('/servico/<nome_servico>')
def servico_escolhido(nome_servico):
    # Consulta a tabela 'PrecoServico' juntando com 'Servico' para filtrar pelo nome do serviço fornecido
    preco_servico = PrecoServico.query.join(Servico).filter(Servico.nomeServico == nome_servico).all()

    try:
        # Inicializa listas para armazenar barbearias, valores dos serviços e IDs dos serviços
        barbearias = []
        valores_servicos = []
        id_servico = []
        
        # Itera sobre os registros de 'preco_servico' encontrados
        for p in preco_servico:
            if p:
                id_barbearia = p.idBarbearia  # Obtém o ID da barbearia associado ao preço do serviço
                barbearia = Barbearia.query.filter_by(idBarbearia=id_barbearia).first()  # Consulta a barbearia pelo ID
                
                if barbearia:
                    barbearias.append(barbearia)  # Adiciona a barbearia à lista
                    valores_servicos.append(p.PrecoServico)  # Adiciona o valor do serviço à lista
                    id_servico.append(p.idPrecoServico)  # Adiciona o ID do preço do serviço à lista
        
        # Renderiza o template 'sistema-homepage.html' passando todos os serviços, as barbearias, os valores dos serviços e o nome do serviço
        return render_template('sistema-homepage.html', servicos=Servico.query.all(), barbearias_valores=zip(barbearias, valores_servicos, id_servico), nome_servico=nome_servico)
    except:
        # Em caso de exceção, exibe uma mensagem de erro e redireciona para a página 'barber'
        flash('Nenhum barbeiro encontrado para o serviço escolhido.', 'error')
        return redirect(url_for('barber'))


@app.route('/agendamentos/<nome_barbearia>/<id_servico>')
@login_required
def agendamento(nome_barbearia, id_servico):
    return render_template('reservar-horario.html', id_servico=id_servico)


# Define a rota '/coletar-agendamento/<int:id_servico>' para a função 'coletar_agendamento' usando o método POST
@app.route('/coletar-agendamento/<int:id_servico>', methods=['POST'])
def coletar_agendamento(id_servico):
    # Coleta os dados do formulário enviados via método POST
    dataAgendamento = request.form['dataAgendamento']  # Data do agendamento
    horaAgendamento = request.form['horaAgendamento']  # Hora do agendamento
    
    # Cria uma nova instância de 'Agenda' com os dados coletados e o ID do serviço fornecido
    nova_agenda = Agenda(idPrecoServico_fk=id_servico, idUsuario_fk=current_user.idUsuario, idStatus_fk=1, dataAtendimento=dataAgendamento, horarioAtendimento=horaAgendamento)
    
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


# Define a rota '/reservas' para a função 'reservasCliente' e exige que o usuário esteja autenticado para acessar
@app.route('/reservas')
@login_required
def reservasCliente():
    # Verifica se o usuário atual está autenticado
    if current_user.is_authenticated:
        id_usuario = current_user.idUsuario  # Obtém o ID do usuário atual

        # Consulta a tabela 'Agenda' para obter todas as reservas feitas pelo usuário atual
        agendas = Agenda.query.filter_by(idUsuario_fk=id_usuario).all()
        
        lista_de_reservas = []  # Inicializa uma lista para armazenar as reservas futuras
        data_atual = datetime.now().date()  # Obtém a data atual
    
        # Itera sobre as reservas do usuário
        for agenda in agendas:
            # Verifica se a data do atendimento é igual ou posterior à data atual
            if agenda.dataAtendimento >= data_atual:
                lista_de_reservas.append(agenda)  # Adiciona a reserva à lista de reservas futuras

    # Renderiza o template 'reservas-clientes.html', passando a lista de reservas futuras
    return render_template('reservas-clientes.html', agendas=lista_de_reservas)


# Define a rota '/agendamentos' para a função 'reservasBarbeiro' e exige que o usuário esteja autenticado para acessar
@app.route('/agendamentos')
@login_required
def reservasBarbeiro():
    # Obtém o ID do usuário logado
    id_usuario_logado = current_user.idUsuario
    print('id do usuario é:', id_usuario_logado)
    
    # Verifica se o usuário é barbeiro
    if current_user.barbeiro == '1':
        print("Este usuário é um barbeiro.")
        id_barbearia_usuario = current_user.idBarbearia_fk  # Obtém o ID da barbearia associada ao usuário
        print('o id da barbearia é:', id_barbearia_usuario)

        # Consulta para verificar as agendas do barbeiro associadas à barbearia
        agenda_usuario = (Agenda.query
                          .join(PrecoServico, Agenda.idPrecoServico_fk == PrecoServico.idPrecoServico)
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
        print("Este usuário não é um barbeiro.")
        # Redireciona o usuário para a página 'barber' se ele não for barbeiro
        return redirect(url_for('barber'))

    
@app.route('/cadastro-servico')
def cadastrarServicos():
    return render_template('cadastrar_servico.html', servicos = Servico.query.all())
    

# Define a função que coleta os serviços do barbeiro e salva no banco
@app.route('/coletar-servicos-barbeiro', methods=['POST'])
def coletarServicosBarbeiro():
    # Obter todos os checkboxes marcados
    servicos_selecionados = request.form.getlist('servico_valor')
    
    servico_valor_pairs = []  # Inicializa uma lista para armazenar pares de serviço e valor

    # Processar os dados do formulário
    for servico_id in servicos_selecionados:
        # Obter o valor do input associado a este serviço
        valor_key = f'valorServico_{servico_id}'
        valor = request.form.get(valor_key, '')
        
        if valor:  # Certifique-se de que há um valor associado
            # Cria uma nova instância de 'PrecoServico' com os dados coletados
            preco_servico_barbeiro = PrecoServico(dataInicio=datetime.now().strftime('%Y-%m-%d'), 
                                                  idBarbearia=current_user.idBarbearia_fk, 
                                                  idServico=servico_id, 
                                                  PrecoServico=valor)
            
            # Adiciona o novo preço de serviço à sessão do banco de dados e confirma a transação
            db.session.add(preco_servico_barbeiro)
            db.session.commit()
            flash('Serviços cadastrados com sucesso!', 'success')
        else:
            # Se algum serviço não tiver valor, exibe uma mensagem de erro e redireciona
            flash('Coloque valor em todos os serviços selecionados.', 'error')
            return redirect(url_for('cadastrarServicos'))

    # Printar os serviços e valores (não necessário para a funcionalidade, mas útil para depuração)
    for servico, valor in servico_valor_pairs:
        print(f'Serviço: {servico}, Valor: {valor}')

    # Redireciona o usuário para a página 'cadastrarServicos' após concluir o processamento
    return redirect(url_for('cadastrarServicos'))


@app.route('/logout')
@login_required
def logout():
    print('Finalizando sessão.')
    logout_user()
    return redirect(url_for('login'))


if "__main__" == __name__:
    app.run(debug = True)