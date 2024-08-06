import Alpine from 'alpinejs';
window.htmx = require('htmx.org');

document.addEventListener("DOMContentLoaded", () => {
    window.Alpine = Alpine;
    Alpine.start();
});