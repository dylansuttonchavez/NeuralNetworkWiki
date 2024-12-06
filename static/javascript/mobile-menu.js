const hamburgerButton = document.getElementById('hamburgerButton');
const closeMenuButton = document.getElementById('closeMenuButton');
const mobileMenu = document.getElementById('mobileMenu');
const menuOverlay = document.getElementById('menuOverlay');
const contentWrapper = document.getElementById('contentWrapper');

const toggleMenu = () => {
    mobileMenu.classList.toggle('-translate-x-full');
    menuOverlay.classList.toggle('opacity-10');
    menuOverlay.classList.toggle('pointer-events-auto');
    contentWrapper.classList.toggle('blur-sm');
};

hamburgerButton.addEventListener('click', toggleMenu);
closeMenuButton.addEventListener('click', toggleMenu);
menuOverlay.addEventListener('click', toggleMenu);