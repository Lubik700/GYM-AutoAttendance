//Login Form
function togglePassword() {
            const passwordInput = document.getElementById('id_password');
            const eyeIcon = document.getElementById('eye-icon');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.innerHTML = `
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                `;
            } else {
                passwordInput.type = 'password';
                eyeIcon.innerHTML = `
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                `;
            }
        }


console.log("JavaScript loaded!");

// Navbar
    function toggleProfileMenu() {
        const menu = document.getElementById('profile-menu');
        const button = document.getElementById('profile-button');
        const isHidden = menu.classList.contains('hidden');

        if (isHidden) {
            menu.classList.remove('hidden');
            button.setAttribute('aria-expanded', 'true');
        } else {
            menu.classList.add('hidden');
            button.setAttribute('aria-expanded', 'false');
        }
    }

    function toggleMobileMenu() {
        const menu = document.getElementById('mobile-menu');
        const openIcon = document.getElementById('menu-open-icon');
        const closeIcon = document.getElementById('menu-close-icon');

        menu.classList.toggle('hidden');
        openIcon.classList.toggle('hidden');
        closeIcon.classList.toggle('hidden');
    }

    // Close profile dropdown when clicking outside
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('profile-dropdown');
        const menu = document.getElementById('profile-menu');
        const button = document.getElementById('profile-button');

        if (dropdown && menu && !dropdown.contains(event.target)) {
            menu.classList.add('hidden');
            if (button) button.setAttribute('aria-expanded', 'false');
        }
    });