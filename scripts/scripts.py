from datetime import datetime, timedelta, time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta


#Função para enviar email de recuperar senha
def enviar_email_recuperar_senha(email: str, codigo: int):
    # Cria o corpo do email com o código de acesso
    corpo_email = f'''     
Código de acesso: {codigo}
'''
    
    # Cria uma instância da mensagem de email
    msg = EmailMessage()
    
    # Define o assunto do email
    msg['Subject'] = "Código de Segurando Ná Regua"
    
    # Define o remetente do email
    msg['From'] = 'jeffinhogamer2014@gmail.com'
    
    # Define o destinatário do email
    msg['To'] = email
    
    # Define a senha do email (neste caso, uma senha de aplicativo do Gmail)
    password = 'tkqt zmfa ypwm gxge'
    
    # Adiciona um cabeçalho indicando que o conteúdo do email é HTML
    msg.add_header('Content-Type', 'text/html')
    
    # Define o corpo do email
    msg.set_payload(corpo_email)
    
    # Configura o servidor de email SMTP para o Gmail
    s = smtplib.SMTP('smtp.gmail.com: 587')
    
    # Inicia a comunicação segura com o servidor de email
    s.starttls()
    
    # Loga na conta de email com o remetente e a senha
    s.login(msg['From'], password)
    
    # Envia o email
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    


def calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas):
    """
    Calcula os horários indisponíveis considerando os horários e durações dos serviços agendados.
    """
    # Inicializa um conjunto para armazenar horários indisponíveis
    horarios_indisponiveis = set()
    
    # Se houver pelo menos um agendamento
    if horarios_agendados:
        # Itera sobre os horários agendados e suas respectivas durações
        for horario, duracao in zip(horarios_agendados, duracoes_agendadas):
            horario_inicio = datetime.strptime(horario, '%H:%M')
            horario_fim = horario_inicio + timedelta(minutes=duracao)
            
            # Marca o intervalo como indisponível
            while horario_inicio < horario_fim:
                horarios_indisponiveis.add(horario_inicio.strftime('%H:%M'))
                horario_inicio += timedelta(minutes=1)  # Avança minuto a minuto
    return horarios_indisponiveis

def verificar_disponibilidade(horario_desejado, duracao_desejada, horarios_indisponiveis):
    """
    Verifica se o horário desejado está disponível para o agendamento.
    """
    horario_inicio = datetime.strptime(horario_desejado, '%H:%M')
    horario_fim = horario_inicio + timedelta(minutes=duracao_desejada)
    
    while horario_inicio < horario_fim:
        if horario_inicio.strftime('%H:%M') in horarios_indisponiveis:
            return False
        horario_inicio += timedelta(minutes=1)  # Verifica a cada minuto
    
    return True

def calcular_horarios_disponiveis(horaInicio, horaFim, duracao, horarios_agendados=None, duracoes_agendadas=None):
    """
    Calcula os horários disponíveis para agendamento dentro de um intervalo de tempo,
    considerando os horários já agendados e suas durações.
    """
    # Combine a data atual com o horário de início e fim para criar objetos datetime
    hoje = datetime.combine(datetime.today(), horaInicio)
    fim = datetime.combine(datetime.today(), horaFim)
    
    # Inicializa a lista de horários disponíveis
    horarios_disponiveis = []
    
    # Verifica se os horários agendados e suas durações foram passados como argumentos
    if horarios_agendados is None:
        horarios_agendados = []
    if duracoes_agendadas is None:
        duracoes_agendadas = []
    
    # Calcula os horários indisponíveis com base nos horários e durações dos serviços agendados
    horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
    
    # Adiciona os horários disponíveis apenas se não estiverem na lista de horários indisponíveis
    while hoje <= fim:
        horario = hoje.time().strftime("%H:%M")
        
        # Verifica se o horário atual não está na lista de horários indisponíveis
        if verificar_disponibilidade(horario, duracao, horarios_indisponiveis):
            horarios_disponiveis.append(horario)
        
        # Avança para o próximo horário com base na duração real do serviço agendado
        hoje += timedelta(minutes=duracao)
        
    return horarios_disponiveis

# Função para adicionar um novo serviço, se possível
def adicionar_servico(horario_desejado, duracao_desejada, horarios_agendados, duracoes_agendadas):
    horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
    disponivel = verificar_disponibilidade(horario_desejado, duracao_desejada, horarios_indisponiveis)

    if disponivel:
        horarios_agendados.append(horario_desejado)
        duracoes_agendadas.append(duracao_desejada)
        print(f"O horário {horario_desejado} foi agendado para um serviço de {duracao_desejada} minutos.")
    else:
        print(f"O horário {horario_desejado} não está disponível para um serviço de {duracao_desejada} minutos.")
    return horarios_agendados, duracoes_agendadas


#Função paraconverter duracao do servico para horas e minutos
def converter_duracao_para_minutos(duracao):
    """
    Converte uma duração no formato 'HH:MM' ou 'MM' para minutos.
    """
    # Verifica se a duração está no formato 'HH:MM'
    if ':' in duracao:
        horas, minutos = map(int, duracao.split(':'))
        return horas * 60 + minutos
    else:
        # Se não, assume que a duração está em minutos
        return int(duracao)

# Teste da função
if __name__ == "__main__":
    
    def calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas):
        """
        Calcula os horários indisponíveis considerando os horários e durações dos serviços agendados.
        """
        # Inicializa um conjunto para armazenar horários indisponíveis
        horarios_indisponiveis = set()
        
        # Se houver pelo menos um agendamento
        if horarios_agendados:
            # Itera sobre os horários agendados e suas respectivas durações
            for horario, duracao in zip(horarios_agendados, duracoes_agendadas):
                horario_inicio = datetime.strptime(horario, '%H:%M')
                horario_fim = horario_inicio + timedelta(minutes=duracao)
                
                # Marca o intervalo como indisponível
                while horario_inicio < horario_fim:
                    horarios_indisponiveis.add(horario_inicio.strftime('%H:%M'))
                    horario_inicio += timedelta(minutes=1)  # Avança minuto a minuto
        return horarios_indisponiveis

    def verificar_disponibilidade(horario_desejado, duracao_desejada, horarios_indisponiveis):
        """
        Verifica se o horário desejado está disponível para o agendamento.
        """
        horario_inicio = datetime.strptime(horario_desejado, '%H:%M')
        horario_fim = horario_inicio + timedelta(minutes=duracao_desejada)
        
        while horario_inicio < horario_fim:
            if horario_inicio.strftime('%H:%M') in horarios_indisponiveis:
                return False
            horario_inicio += timedelta(minutes=1)  # Verifica a cada minuto
        
        return True

    def calcular_horarios_disponiveis(horaInicio, horaFim, duracao, horarios_agendados=None, duracoes_agendadas=None):
        """
        Calcula os horários disponíveis para agendamento dentro de um intervalo de tempo,
        considerando os horários já agendados e suas durações.
        """
        # Combine a data atual com o horário de início e fim para criar objetos datetime
        hoje = datetime.combine(datetime.today(), horaInicio)
        fim = datetime.combine(datetime.today(), horaFim)
        
        # Inicializa a lista de horários disponíveis
        horarios_disponiveis = []
        
        # Verifica se os horários agendados e suas durações foram passados como argumentos
        if horarios_agendados is None:
            horarios_agendados = []
        if duracoes_agendadas is None:
            duracoes_agendadas = []
        
        # Calcula os horários indisponíveis com base nos horários e durações dos serviços agendados
        horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
        
        # Adiciona os horários disponíveis apenas se não estiverem na lista de horários indisponíveis
        while hoje <= fim:
            horario = hoje.time().strftime("%H:%M")
            
            # Verifica se o horário atual não está na lista de horários indisponíveis
            if verificar_disponibilidade(horario, duracao, horarios_indisponiveis):
                horarios_disponiveis.append(horario)
            
            # Avança para o próximo horário com base na duração real do serviço agendado
            hoje += timedelta(minutes=duracao)
            
        return horarios_disponiveis

    # Função para adicionar um novo serviço, se possível
    def adicionar_servico(horario_desejado, duracao_desejada, horarios_agendados, duracoes_agendadas):
        horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
        disponivel = verificar_disponibilidade(horario_desejado, duracao_desejada, horarios_indisponiveis)

        if disponivel:
            horarios_agendados.append(horario_desejado)
            duracoes_agendadas.append(duracao_desejada)
            print(f"O horário {horario_desejado} foi agendado para um serviço de {duracao_desejada} minutos.")
        else:
            print(f"O horário {horario_desejado} não está disponível para um serviço de {duracao_desejada} minutos.")
        return horarios_agendados, duracoes_agendadas

