
function mostraropcoes(opcao) {
    var horarioSim = document.getElementById("horario_sim");
    var horarioNao = document.getElementById("horario_nao");
    var nomeBarbearia = document.getElementById("nomeBarbearia");
    var rua = document.getElementById("rua");
    var numero = document.getElementById("numero");
    var bairro = document.getElementById("bairro");
    var cidade = document.getElementById("cidade");
    var estado = document.getElementById("estado");
    var titulosim = document.getElementById("titulo");
    var btn_barbeiro = document.getElementById("btn_barbeiro");
    var btn_barbearia = document.getElementById("btn_barbearia");
    var telefoneBarbearia = document.getElementById("telefoneBarbearia");
    var cep = document.getElementById("cep");

    if (opcao === "sim") {
        horarioSim.style.display = "block";
        nomeBarbearia.style.display = "block";
        rua.style.display = "block";
        numero.style.display = "block";
        bairro.style.display = "block";
        cidade.style.display = "block";
        estado.style.display = "block";
        titulosim.style.display = "block";
        btn_barbearia.style.display = "block";
        telefoneBarbearia.style.display = "block";
        cep.style.display = "block";
        btn_barbeiro.style.display = "none";
        horarioNao.style.display = "none"

    } else {

        horarioSim.style.display = "none";
        nomeBarbearia.style.display = "none"
        rua.style.display = "none";
        numero.style.display = "none";
        bairro.style.display = "none";
        cidade.style.display = "none";
        estado.style.display = "none";
        titulosim.style.display = "none";
        telefoneBarbearia.style.display = "none";
        btn_barbearia.style.display = "none";
        cep.style.display = "none";
        btn_barbeiro.style.display = "block";
        horarioNao.style.display = "block";

    }
}