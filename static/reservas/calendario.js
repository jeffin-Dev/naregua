document.addEventListener('DOMContentLoaded', function () {
    const calendario = document.getElementById('calendario');
    const horariosContainer = document.getElementById('horarios-container');
    const horariosSelect = document.getElementById('horarios');
    
    // Função para carregar os horários disponíveis com base na data selecionada
    function carregarHorariosDisponiveis(dataSelecionada) {
        const xhr = new XMLHttpRequest();
        const idServico = document.getElementById('id_servico').value;
        xhr.open('GET', `/agendamentos/horarios-disponiveis?data=${dataSelecionada}&id_servico=${idServico}`, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                const horariosDisponiveis = JSON.parse(xhr.responseText);
                horariosSelect.innerHTML = '';
                horariosDisponiveis.forEach(function(horario) {
                    const option = document.createElement('option');
                    option.value = horario;
                    option.textContent = horario;
                    horariosSelect.appendChild(option);
                });
                horariosContainer.style.display = 'block';
            }
        };
        xhr.send();
    }

    // Configurar o flatpickr para atualizar os horários disponíveis quando uma nova data for selecionada
    flatpickr(calendario, {
        locale: 'pt-br',
        dateFormat: 'Y-m-d',
        onChange: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                const dataSelecionada = selectedDates[0].toISOString().split('T')[0];
                carregarHorariosDisponiveis(dataSelecionada);
            }
        }
    });
});
