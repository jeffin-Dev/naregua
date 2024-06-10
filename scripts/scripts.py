from datetime import datetime, timedelta, time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta


#Função para enviar email de recuperar senha:
def enviar_email_recuperar_senha(email: str, codigo: int):
    # Cria o corpo do email com o código de acesso
    corpo_email = f'''     
Código de acesso: {codigo}
'''
    
    # Cria uma instância da mensagem de email
    msg = EmailMessage()
    
    # Define o assunto do email
    msg['Subject'] = "Código de Segurança para troca de senha Ná Regua"
    
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
    

#Função para calcular os horarios indisponpíveis:
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


#Função para verificar a disponibilidade:
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


#Função para calcular horarios disponíveis:
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


# Função para adicionar um serviço a um horário desejado
def adicionar_servico(horario_desejado, duracao_desejada, horarios_agendados, duracoes_agendadas):
    # Calcular horários indisponíveis com base nos horários e durações já agendados
    horarios_indisponiveis = calcular_horarios_indisponiveis(horarios_agendados, duracoes_agendadas)
    
    # Verificar se o horário desejado está disponível
    disponivel = verificar_disponibilidade(horario_desejado, duracao_desejada, horarios_indisponiveis)

    # Se o horário estiver disponível, adiciona-o às listas de horários e durações agendadas
    if disponivel:
        horarios_agendados.append(horario_desejado)
        duracoes_agendadas.append(duracao_desejada)
        print(f"O horário {horario_desejado} foi agendado para um serviço de {duracao_desejada} minutos.")
    else:
        # Caso contrário, informa que o horário não está disponível
        print(f"O horário {horario_desejado} não está disponível para um serviço de {duracao_desejada} minutos.")
    
    # Retorna as listas atualizadas de horários e durações agendadas
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
    
    
#Função para simplificar o endereço passado para a geolocalização
def endereco_cliente_simplificado(address_parts):
    endereco_simplificado_parts = [
        address_parts.get('road', ''), 
        address_parts.get('house_number', ''),  
        address_parts.get('suburb', ''),
        address_parts.get('city', ''),
        address_parts.get('state', ''),
        address_parts.get('country', '')
    ]
    
    #Faz o tratamento de campos em branco:
    endereco_simplificado = ', '.join(part for part in endereco_simplificado_parts if part)
    
    return endereco_simplificado




# Teste da função
if __name__ == "__main__":
    pass