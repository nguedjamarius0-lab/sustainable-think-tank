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
    const btnFooter = document.getElementById('theme-toggle-footer');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    if (btnFooter) {
        const iconFooter = document.getElementById('theme-icon-footer');
        if (iconFooter) {
            iconFooter.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        const textNode = btnFooter.childNodes[btnFooter.childNodes.length - 1];
        if (textNode && textNode.nodeType === 3) {
            textNode.textContent = theme === 'dark' ? ' Mode clair' : ' Mode sombre';
        }
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
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
        navLinks.classList.toggle('open');
        hamburger.classList.toggle('active');
    });

    // Close menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            hamburger.classList.remove('active');
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
            navLinks.classList.remove('open');
            hamburger.classList.remove('active');
        }
    });

    // Close menu on Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navLinks.classList.contains('open')) {
            navLinks.classList.remove('open');
            hamburger.classList.remove('active');
        }
    });
}

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

// Close user menu on outside click
document.addEventListener('click', function(e) {
    const userMenu = document.querySelector('.user-menu');
    if (userMenu && !userMenu.contains(e.target)) {
        userMenu.classList.remove('open');
    }
});

// Flash messages auto-dismiss with close button
document.querySelectorAll('.flash').forEach(flash => {
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'flash-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.setAttribute('aria-label', 'Fermer');
    closeBtn.addEventListener('click', function() {
        flash.style.opacity = '0';
        flash.style.transform = 'translateY(-10px)';
        setTimeout(() => flash.remove(), 300);
    });
    flash.appendChild(closeBtn);

    // Auto dismiss after 8 seconds
    setTimeout(() => {
        if (flash.parentNode) {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => flash.remove(), 300);
        }
    }, 8000);
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
