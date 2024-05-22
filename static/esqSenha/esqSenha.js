function enviarEmail() {
    var email = document.getElementById("email").value;
    var message = document.getElementById("message");
    message.innerHTML = "Um e-mail de redefinição de senha foi enviado para " + email;
}
