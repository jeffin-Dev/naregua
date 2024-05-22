from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomeUsuario = db.Column(db.String(100))
    cpf = db.Column(db.String(15), primary_key=True)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(45))
    senha = db.Column(db.String(12))
    barbeiro = db.Column(db.Integer)
    idBarbeiro = db.Column(db.Integer, db.ForeignKey('barbearia.idBarbearia'))
    
    
    barbearia = db.relationship('Barbearia', foreign_keys=[idBarbeiro], backref=db.backref('usuarios', lazy=True))
    
    
    def is_authenticated(self):
        # Lógica para determinar se o usuário está autenticado
        return True  # ou False, dependendo da lógica de autenticação

    def is_active(self):
        # Lógica para determinar se o usuário está ativo ou não
        return True  # ou False, dependendo da lógica de ativação


    def get_id(self):
        # Lógica para pegar o cpf do usuario
        return str(self.cpf)
    


class Barbearia(db.Model):
    __tablename__ = 'barbearia'

    idBarbearia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'))
    nomeBarbearia = db.Column(db.String(45))
    endereco = db.Column(db.String(150))
    telefone = db.Column(db.String(20))
    horaInicio = db.Column(db.Time())
    horaFim = db.Column(db.Time())
    
    
    def get_id(self):
        # Lógica para pegar o cpf do barbeiro
        return str(self.id_usuario)    

class Agenda(db.Model):
    __tablename__ = 'agenda'
    
    idReserva = db.Column(db.Integer, primary_key=True)
    idPrecoServico = db.Column(db.Integer, db.ForeignKey('preco_servico.codPrecoServico'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    idStatus = db.Column(db.Integer, db.ForeignKey('status.idStatus'), nullable=False)
    dataAtendimento = db.Column(db.Date, nullable=False)
    horarioAtendimento = db.Column(db.Time, nullable=False)
    
    # Relacionamentos opcionais
    preco_servico = db.relationship('PrecoServico', backref=db.backref('agendas', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('agendas', lazy=True))
    status = db.relationship('Status', backref=db.backref('agendas', lazy=True))
    
    def __init__(self, idPrecoServico, idUsuario, idStatus, dataAtendimento, horarioAtendimento):
        self.idPrecoServico = idPrecoServico
        self.idUsuario = idUsuario
        self.idStatus = idStatus
        self.dataAtendimento = dataAtendimento
        self.horarioAtendimento = horarioAtendimento

    def __repr__(self):
        return f'<Agenda {self.idReserva}>'
    
    
class Status(db.Model):
    __tablename__ = 'status'
    
    idStatus = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(50))
    

class PrecoServico(db.Model):
    __tablename__ = 'preco_servico'
    
    codPrecoServico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataInicio = db.Column(db.Date, nullable=False)
    idBarbearia = db.Column(db.Integer, db.ForeignKey('barbearia.idBarbearia'), nullable=False)
    idServico = db.Column(db.Integer, db.ForeignKey('servico.idServico'), nullable=False)
    PrecoServico = db.Column(db.Float, nullable=False)
    
    #Relações pela tabela Preco_Servico
    servico = db.relationship('Servico', backref=db.backref('precos_servico', lazy=True))
    barbearia = db.relationship('Barbearia', backref=db.backref('precos_servico', lazy=True))
    
    
class Servico(db.Model):
    __tablename__ = 'servico'
    
    idServico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nomeServico = db.Column(db.String(250), nullable=False)