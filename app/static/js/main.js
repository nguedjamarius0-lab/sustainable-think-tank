// Theme toggle
function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcons(newTheme);
}

function updateThemeIcons(theme) {
    const icon = document.getElementById('theme-icon');
    const iconFooter = document.getElementById('theme-icon-footer');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    if (iconFooter) {
        iconFooter.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        iconFooter.nextElementSibling && (iconFooter.parentElement.textContent = theme === 'dark' ? ' Mode clair' : ' Mode sombre');
    }
}

// Load saved theme
(function() {
    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcons(saved);
})();

// Active nav link
document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active');
    }
});

// Mobile menu toggle
document.querySelector('.hamburger')?.addEventListener('click', function() {
    document.querySelector('.nav-links').classList.toggle('open');
});

// Password toggle
function togglePassword(id, btn) {
    const input = document.getElementById(id);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// User menu toggle
document.querySelector('.user-menu-btn')?.addEventListener('click', function() {
    this.parentElement.classList.toggle('open');
});

// Flash messages auto-dismiss
document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
        flash.style.opacity = '0';
        flash.style.transform = 'translateY(-10px)';
        setTimeout(() => flash.remove(), 300);
    }, 5000);
});

// ===== PWA Service Worker + Install Banner =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js').catch(() => {});
    });
}

(function() {
    let deferredPrompt = null;
    const banner = document.getElementById('pwa-install-banner');
    const installBtn = document.getElementById('pwa-install-btn');
    const dismissBtn = document.getElementById('pwa-dismiss-btn');

    if (!banner) return;

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
    });

    if (installBtn) {
        installBtn.addEventListener('click', () => {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(() => {
                deferredPrompt = null;
                hideBannerForever();
            });
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            hideBannerForever();
        });
    }

    window.addEventListener('appinstalled', () => {
        hideBannerForever();
        deferredPrompt = null;
    });

    function showBanner() {
        banner.style.display = 'block';
        document.body.classList.add('pwa-banner-visible');
        setTimeout(() => {
            banner.style.display = 'none';
            document.body.classList.remove('pwa-banner-visible');
        }, 30000);
    }

    function hideBannerForever() {
        banner.style.display = 'none';
        document.body.classList.remove('pwa-banner-visible');
        clearInterval(window.__pwaLoop);
    }

    window.__pwaLoop = setInterval(showBanner, 120000);
    showBanner();
})();
