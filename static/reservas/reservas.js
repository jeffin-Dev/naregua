document.addEventListener('DOMContentLoaded', function () {
    const reservas = [
        {
            id: 1,
            servico: 'Corte de Cabelo',
            data: '2024-05-20',
            hora: '14:00',
            barbearia: 'Barbearia do João',
            status: 'Aguardando confirmação...'
        },
        {
            id: 2,
            servico: 'Barba',
            data: '2024-05-22',
            hora: '16:00',
            barbearia: 'Barbearia do Pedro',
            status: 'Reservado'
        },
        {
            id: 3,
            servico: 'Corte de Cabelo e Barba',
            data: '2024-05-25',
            hora: '10:00',
            barbearia: 'Barbearia do José',
            status: 'Cancelado'
        }
    ];

    const reservasContainer = document.getElementById('reservas-container');

    reservas.forEach(reserva => {
        const card = document.createElement('div');
        card.classList.add('card');

        card.innerHTML = `
            <h2>${reserva.servico}</h2>
            <p><strong>Data:</strong> ${reserva.data}</p>
            <p><strong>Hora:</strong> ${reserva.hora}</p>
            <p><strong>Barbearia:</strong> ${reserva.barbearia}</p>
            <p><strong>Status:</strong><span class="status-text" id="status-${reserva.id}">${reserva.status}</span></p>
            <button class="btn-cancelar" onclick="cancelarReserva(${reserva.id})">Cancelar</button>
        `;

        reservasContainer.appendChild(card);
    });
});

function cancelarReserva(reservaId) {
    const confirmCancel = confirm('Você realmente quer cancelar esta reserva?');
    if (confirmCancel) {
        const statusElement = document.getElementById(`status-${reservaId}`);
        statusElement.textContent = 'Cancelado';
        alert('Reserva Cancelada!');
    }
}
