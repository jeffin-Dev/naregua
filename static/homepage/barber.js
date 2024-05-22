// Abrir modal de cadastro de serviço de barbearia
function openBarberForm() {
    document.getElementById("barber-modal").style.display = "block";
}

// Fechar modal de cadastro de serviço de barbearia
function closeBarberForm() {
    document.getElementById("barber-modal").style.display = "none";
}

// Submeter formulário de cadastro de serviço de barbearia
document.getElementById("barber-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Evitar que o formulário seja submetido normalmente

    // Aqui você pode adicionar a lógica para enviar os dados do formulário para o backend ou fazer o que for necessário com eles
    // Por exemplo, você pode usar JavaScript para validar os campos do formulário antes de enviar os dados
    // e depois enviar esses dados para o servidor através de uma requisição AJAX
    // ou redirecionar o usuário para outra página após o envio bem-sucedido do formulário
    // Por enquanto, vou apenas imprimir os dados do formulário no console para fins de demonstração
    const serviceName = document.getElementById("service-name").value;
    const price = document.getElementById("price").value;
    console.log("Nome do Serviço:", serviceName);
    console.log("Preço:", price);

    // Fechar o modal após o envio do formulário
    closeBarberForm();
});
