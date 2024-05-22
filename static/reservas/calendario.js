document.addEventListener('DOMContentLoaded', function () {
    const calendario = document.getElementById('calendario');
    const horariosContainer = document.getElementById('horarios-container');
    const horariosSelect = document.getElementById('horarios');

    flatpickr(calendario, {
        locale: 'pt',
        dateFormat: 'Y-m-d',
        onChange: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                const selectedDate = selectedDates[0];
                horariosSelect.innerHTML = '';
                const startTime = 8 * 60; // 08:00 em minutos
                const endTime = 17 * 60 + 30; // 17:30 em minutos
                for (let time = startTime; time <= endTime; time += 30) {
                    const hours = Math.floor(time / 60);
                    const minutes = time % 60;
                    const timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
                    const option = document.createElement('option');
                    option.value = timeStr;
                    option.textContent = timeStr;
                    horariosSelect.appendChild(option);
                }
                horariosContainer.style.display = 'block';
            }
        }
    });

    horariosSelect.addEventListener('change', function () {
        const selectedDate = calendario.value;
        const selectedTime = horariosSelect.value;
        if (selectedDate && selectedTime) {
            const dateParts = selectedDate.split('-');
            const formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;
        }
    });
});
