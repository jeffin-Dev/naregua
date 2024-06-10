var header = document.getElementById('header');
var navigationHeader = document.getElementById('navigation_header');
var content = document.getElementById('content');
var showSidebar = false;

function toggleSidebar() {
    showSidebar = !showSidebar;
    if (showSidebar) {
        navigationHeader.style.marginLeft = '-3vw';
        navigationHeader.style.animationName = 'showSidebar';
        content.style.filter = 'blur(2px)';
    }
    else {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
    }
}

function closeSidebar() {
    if (showSidebar) {
        toggleSidebar();
    }
}

window.addEventListener('resize', function (event) {
    if (window.innerWidth > 768 && showSidebar) {
        toggleSidebar();
    }
});

// Função para alternar a barra lateral de navegação
var showSidebar = false;
function toggleSidebar() {
    showSidebar = !showSidebar;
    const navigationHeader = document.getElementById('navigation_header');
    const content = document.getElementById('content');
    if (showSidebar) {
        navigationHeader.style.marginLeft = '-3vw';
        navigationHeader.style.animationName = 'showSidebar';
        content.style.filter = 'blur(2px)';
    } else {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
    }
}

// Fechar a barra lateral ao redimensionar a janela
window.addEventListener('resize', function (event) {
    const navigationHeader = document.getElementById('navigation_header');
    const content = document.getElementById('content');
    if (window.innerWidth > 768 && showSidebar) {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
        showSidebar = false;
    }
});



var header = document.getElementById('header');
var navigationHeader = document.getElementById('navigation_header');
var content = document.getElementById('content');
var showSidebar = false;

function toggleSidebar() {
    showSidebar = !showSidebar;
    if (showSidebar) {
        navigationHeader.style.marginLeft = '-3vw';
        navigationHeader.style.animationName = 'showSidebar';
        content.style.filter = 'blur(2px)';
    }
    else {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
    }
}

function closeSidebar() {
    if (showSidebar) {
        toggleSidebar();
    }
}

window.addEventListener('resize', function (event) {
    if (window.innerWidth > 768 && showSidebar) {
        toggleSidebar();
    }
});

// Função para alternar a barra lateral de navegação
var showSidebar = false;
function toggleSidebar() {
    showSidebar = !showSidebar;
    const navigationHeader = document.getElementById('navigation_header');
    const content = document.getElementById('content');
    if (showSidebar) {
        navigationHeader.style.marginLeft = '-3vw';
        navigationHeader.style.animationName = 'showSidebar';
        content.style.filter = 'blur(2px)';
    } else {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
    }
}

// Fechar a barra lateral ao redimensionar a janela
window.addEventListener('resize', function (event) {
    const navigationHeader = document.getElementById('navigation_header');
    const content = document.getElementById('content');
    if (window.innerWidth > 768 && showSidebar) {
        navigationHeader.style.marginLeft = '-100vw';
        navigationHeader.style.animationName = '';
        content.style.filter = '';
        showSidebar = false;
    }
});



document.addEventListener('DOMContentLoaded', function () {
    var cancelModal = document.getElementById('cancelModal');
    var confirmCancelBtn = document.getElementById('confirmCancelBtn');
    var cancelUrl = '';

    cancelModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        cancelUrl = button.getAttribute('data-url');
    });

    confirmCancelBtn.addEventListener('click', function () {
        window.location.href = cancelUrl;
    });
});
