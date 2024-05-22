function login() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (username === "usuario" && password === "senha") {
        window.location.href = "./sistema-homepage.html";
    } else {
        alert("Usuário ou senha incorretos. Tente novamente.");
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const showPasswordBtn = document.getElementById('showPasswordBtn');
    const passwordInput = document.getElementById('password');

    showPasswordBtn.addEventListener('click', function () {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            showPasswordBtn.textContent = 'Esconder';
        } else {
            passwordInput.type = 'password';
            showPasswordBtn.textContent = 'Mostrar';
        }
    });
});

function checkInput(input) {
    // Verifica se o valor inserido parece ser um número de telefone
    if (/^\d{10,11}$/.test(input.value)) {
        // Se for um número, chama a função formatPhoneNumber
        formatPhoneNumber(input);
    }
}

function formatPhoneNumber(input) {
    let numbers = input.value.replace(/\D/g, ''); // Remove todos os caracteres não numéricos
    let formattedNumber = '';

    if (numbers.length > 0) {
        // Formatação para o código de área
        formattedNumber = '(' + numbers.substring(0, 2) + ') ';
    }

    if (numbers.length > 2) {
        // Formatação para o número principal
        formattedNumber += numbers.substring(2, 3) + ' ';
        if (numbers.length > 3) {
            formattedNumber += numbers.substring(3, 7);
            if (numbers.length > 7) {
                // Formatação para o número final
                formattedNumber += '-' + numbers.substring(7, 11);
            }
        }
    }

    input.value = formattedNumber;
}