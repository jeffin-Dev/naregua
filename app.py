from flask import Flask, render_template, flash, redirect, url_for, request
from model import db, Usuario, Agenda, Barbearia, PrecoServico
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

# Esta função é uma rota Flask que recebe os dados de cadastro de um formulário HTML via método POST.
@app.route('/coletar-cadastro', methods=['POST'])
def coletar_cadastro():
    # Obtém os dados do formulário enviado.
    nomeCompleto = request.form['nomeCompleto']
    cpf = request.form['cpf']
    telefone = request.form['telefone']
    email = request.form['email']
    senha1 = request.form['senha1']
    senha2 = request.form['senha2']

    # Verifica se algum campo obrigatório está em branco.
    if (nomeCompleto == '') or (telefone == '') or (email == '') or (senha1 == '') or (senha2 == ''):
        print('Houve algum campo em branco.')
        # Redireciona de volta para a página de cadastro.
        return redirect(url_for('cadastrar'))
    else:
        # Verifica se as senhas fornecidas coincidem.
        if str(senha1) == str(senha2):
            # Formata os dados antes de criar um novo usuário.
            nomeCompleto = nomeCompleto.capitalize()
            email = email.lower()

            # Cria um novo objeto de usuário com os dados fornecidos.
            novo_usuario = Usuario(cpf=cpf, nomeCompleto=nomeCompleto, email=email, telefone=telefone, senha=senha1, barbeiro = False)
            
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


@app.route('/coletar-cadastro-barbeiro', methods=['POST'])
def coletar_cadastro_barbeiro():
    if current_user.is_authenticated:
        id_usuario = current_user.idUsuario
        print('O id do user é:', id_usuario)
    
    nomeBarbearia = request.form['nomeBarbearia']
    telefone = request.form['telefone']
    rua = request.form['rua']
    numero = request.form['numero']
    bairro = request.form['bairro']
    cep = request.form['cep']
    cidade = request.form['cidade']
    estado = request.form['estado']
    horaInicio = request.form['horario_abertura_sim']
    horaFim = request.form['horario_fechamento_sim']
    barbeiro = True
    
    endereco = f'{rua}, {numero} - {bairro}, CEP: {cep} - {cidade}, {estado}'
    
    novoBarbeiro = Barbearia(idUsuario=id_usuario, nomeBarbearia=nomeBarbearia, telefone=telefone, endereco=endereco, horaInicio=horaInicio, horaFim=horaFim)
    
    db.session.add(novoBarbeiro)
    
    usuario = Usuario.query.filter_by(idUsuario=id_usuario).first()
    if usuario:
        
        usuario.barbeiro = True

    db.session.commit()
    print(f'''
Cadastro feito!!
Nome: {nomeBarbearia}.
Endereço: {endereco}.
Telefone: {telefone}.
Horario de abertura: {horaInicio}.
Horario de fechamento: {horaFim}.
Barberiro? {barbeiro}.
''')
    
    

    return redirect(url_for('barber'))
    

@app.route('/esq-senha')
def esq_senha():
    return render_template('esqueci_minha_senha.html')

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


@app.route('/home-barbearia')
@app.route('/')
def barber():
    if current_user.is_authenticated:
        barbeiro = int(current_user.barbeiro)
        print(barbeiro, type(barbeiro))
        return render_template('sistema-homepage.html', barbeiro = barbeiro)
    else:
        return render_template('sistema-homepage.html')


@app.route('/agendamentos/barbeiro')
@login_required
def agendamento():
    return render_template('reservar-horario.html')

@app.route('/coletar-agendamento', methods=['POST'])
def coletar_agendamento():
    dataAgendamento = request.form['dataAgendamento']
    horaAgendamento = request.form['horaAgendamento']
    
    nova_agenda = Agenda(idPrecoServico= 1, idUsuario=1, idStatus=1, dataAtendimento=dataAgendamento, horarioAtendimento=horaAgendamento)
    db.session.add(nova_agenda)
    db.session.commit()
    
    print('Você agendou um corte da data:', dataAgendamento, '\nO horario do agendamento é: ', horaAgendamento)
    return redirect(url_for('agendamento'))


@app.route('/reservas')
@login_required
def reservasCliente():
    if current_user.is_authenticated:
        id_usuario = current_user.idUsuario
        reservas = Agenda.query.filter_by(idUsuario=id_usuario).all()
        
        lista_de_reservas = []
        data_atual = datetime.now().date()
    
        for reserva in reservas:
            if reserva.dataAtendimento >= data_atual:
                lista_de_reservas.append(reserva)

    return render_template('reservas-clientes.html', reservas=lista_de_reservas)

@app.route('/agendamentos')
@login_required
def reservasBarbeiro():
    id_barbearia = current_user.barbearia.idBarbearia if current_user.barbearia else None
    lista_de_agendamentos = []
    data_atual = datetime.now().date()

    if id_barbearia:
        
        # Consulta de agendamentos para a barbearia atual
        agendamentos = Agenda.query.join(PrecoServico).join(Barbearia).filter(PrecoServico.idBarbearia == id_barbearia).all()
        
        for agendamento in agendamentos:
            if agendamento.dataAtendimento >= data_atual:
                lista_de_agendamentos.append(agendamento)
        
    
    return render_template('reservas-barbeiro.html', agendamentos=lista_de_agendamentos)
    

@app.route('/logout')
@login_required
def logout():
    print('Finalizando sessão.')
    logout_user()
    return redirect(url_for('login'))


if "__main__" == __name__:
    app.run(debug = True)