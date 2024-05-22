function autenticarEmail() {
    var email = document.getElementById("email").value;
    var message = document.getElementById("message");
    if (email === "exemplo@email.com") {
        window.location.href = "criar_senha.html";
    } else {
        message.innerHTML = "O e-mail fornecido não foi autenticado. Tente novamente.";
    }
}
