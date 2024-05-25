from flask_sqlalchemy import SQLAlchemy

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy()

# Define a classe 'Usuario', que representa a tabela 'usuario' no banco de dados
class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    # Define as colunas da tabela 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária com incremento automático
    nomeUsuario = db.Column(db.String(100))  # Coluna para armazenar o nome do usuário
    cpf = db.Column(db.String(15), primary_key=True)  # Coluna para armazenar o CPF do usuário, também usado como chave primária
    telefone = db.Column(db.String(20))  # Coluna para armazenar o telefone do usuário
    email = db.Column(db.String(45))  # Coluna para armazenar o email do usuário
    senha = db.Column(db.String(12))  # Coluna para armazenar a senha do usuário
    barbeiro = db.Column(db.String(1), default='0')  # Coluna para indicar se o usuário é barbeiro (0 ou 1)
    idBarbearia_fk = db.Column(db.Integer)  # Coluna para armazenar a referência à barbearia
    
    def is_authenticated(self):
        # Lógica para determinar se o usuário está autenticado
        return True  # ou False, dependendo da lógica de autenticação

    def is_active(self):
        # Lógica para determinar se o usuário está ativo ou não
        return True  # ou False, dependendo da lógica de ativação

    def get_id(self):
        # Lógica para pegar o CPF do usuário
        return str(self.cpf)

# Define a classe 'Barbearia', que representa a tabela 'barbearia' no banco de dados
class Barbearia(db.Model):
    __tablename__ = 'barbearia'

    # Define as colunas da tabela 'barbearia'
    idBarbearia = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária com incremento automático
    nomeBarbearia = db.Column(db.String(45))  # Coluna para armazenar o nome da barbearia
    endereco = db.Column(db.String(150))  # Coluna para armazenar o endereço da barbearia
    telefone = db.Column(db.String(20))  # Coluna para armazenar o telefone da barbearia
    horaInicio = db.Column(db.Time())  # Coluna para armazenar a hora de início do funcionamento
    horaFim = db.Column(db.Time())  # Coluna para armazenar a hora de fim do funcionamento

    def get_id(self):
        # Lógica para pegar o ID da barbearia
        return str(self.id_usuario)

# Define a classe 'Agenda', que representa a tabela 'agenda' no banco de dados
class Agenda(db.Model):
    __tablename__ = 'agenda'
    
    # Define as colunas da tabela 'agenda'
    idReserva = db.Column(db.Integer, primary_key=True)  # Chave primária
    idPrecoServico_fk = db.Column(db.Integer, db.ForeignKey('preco_servico.idPrecoServico'), nullable=False)  # Chave estrangeira para 'preco_servico'
    idUsuario_fk = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)  # Chave estrangeira para 'usuario'
    idStatus_fk = db.Column(db.Integer, db.ForeignKey('status.idStatus'), nullable=False)  # Chave estrangeira para 'status'
    dataAtendimento = db.Column(db.Date, nullable=False)  # Coluna para armazenar a data do atendimento
    horarioAtendimento = db.Column(db.Time, nullable=False)  # Coluna para armazenar o horário do atendimento
    
    # Relacionamentos opcionais
    preco_servico_fk = db.relationship('PrecoServico', backref=db.backref('agendas', lazy=True))  # Relacionamento com 'PrecoServico'
    usuario_fk = db.relationship('Usuario', backref=db.backref('agendas', lazy=True))  # Relacionamento com 'Usuario'
    status_fk = db.relationship('Status', backref=db.backref('agendas', lazy=True))  # Relacionamento com 'Status'
    
    def __init__(self, idPrecoServico_fk, idUsuario_fk, idStatus_fk, dataAtendimento, horarioAtendimento):
        # Inicializa uma nova instância de 'Agenda'
        self.idPrecoServico_fk = idPrecoServico_fk
        self.idUsuario_fk = idUsuario_fk
        self.idStatus_fk = idStatus_fk
        self.dataAtendimento = dataAtendimento
        self.horarioAtendimento = horarioAtendimento

    def __repr__(self):
        # Representação string da instância 'Agenda'
        return f'<Agenda {self.idReserva}>'

# Define a classe 'Status', que representa a tabela 'status' no banco de dados
class Status(db.Model):
    __tablename__ = 'status'
    
    # Define as colunas da tabela 'status'
    idStatus = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária com incremento automático
    descricao = db.Column(db.String(50))  # Coluna para armazenar a descrição do status

# Define a classe 'PrecoServico', que representa a tabela 'preco_servico' no banco de dados
class PrecoServico(db.Model):
    __tablename__ = 'preco_servico'
    
    # Define as colunas da tabela 'preco_servico'
    idPrecoServico = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária com incremento automático
    dataInicio = db.Column(db.Date, nullable=False)  # Coluna para armazenar a data de início do serviço
    idBarbearia = db.Column(db.Integer, db.ForeignKey('barbearia.idBarbearia'), nullable=False)  # Chave estrangeira para 'barbearia'
    idServico = db.Column(db.Integer, db.ForeignKey('servico.idServico'), nullable=False)  # Chave estrangeira para 'servico'
    PrecoServico = db.Column(db.Float, nullable=False)  # Coluna para armazenar o preço do serviço
    
    # Relacionamentos pela tabela 'PrecoServico'
    servico = db.relationship('Servico', backref=db.backref('precos_servico', lazy=True))  # Relacionamento com 'Servico'
    barbearia = db.relationship('Barbearia', backref=db.backref('precos_servico', lazy=True))  # Relacionamento com 'Barbearia'

# Define a classe 'Servico', que representa a tabela 'servico' no banco de dados
class Servico(db.Model):
    __tablename__ = 'servico'
    
    # Define as colunas da tabela 'servico'
    idServico = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Chave primária com incremento automático
    nomeServico = db.Column(db.String(250), nullable=False)  # Coluna para armazenar o nome do serviço
