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
    const icons = document.querySelectorAll('[id^="theme-icon"]');
    icons.forEach(icon => {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    });

    const btnFooter = document.getElementById('theme-toggle-footer');
    if (btnFooter) {
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

// Sidebar toggle (mobile)
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
const sidebarClose = document.getElementById('sidebar-close');
const sidebarOverlay = document.getElementById('sidebar-overlay');

function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

if (hamburger) hamburger.addEventListener('click', openSidebar);
if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

// Close sidebar on Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
    }
});

// Close sidebar when clicking a nav link (mobile)
if (sidebar) {
    sidebar.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) closeSidebar();
        });
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
document.querySelectorAll('.user-menu-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        this.parentElement.classList.toggle('open');
    });
});

// Close user menu on outside click
document.addEventListener('click', function(e) {
    document.querySelectorAll('.user-menu.open').forEach(menu => {
        if (!menu.contains(e.target)) {
            menu.classList.remove('open');
        }
    });
});

// Flash messages with close button
document.querySelectorAll('.flash').forEach(flash => {
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

    setTimeout(() => {
        if (flash.parentNode) {
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(() => flash.remove(), 300);
        }
    }, 8000);
});

// ===== PWA =====
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
    const iosBanner = document.getElementById('ios-install-hint');
    const iosDismissBtn = document.getElementById('ios-dismiss-btn');

    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

    if (isStandalone) return;

    // iOS: show manual install hint
    if (isIOS && iosBanner) {
        const dismissed = localStorage.getItem('pwa_ios_dismissed');
        if (!dismissed) {
            iosBanner.style.display = 'block';
            document.body.classList.add('pwa-banner-visible');
        }
        if (iosDismissBtn) {
            iosDismissBtn.addEventListener('click', () => {
                iosBanner.style.display = 'none';
                document.body.classList.remove('pwa-banner-visible');
                localStorage.setItem('pwa_ios_dismissed', '1');
            });
        }
        return;
    }

    // Android / Chrome: use beforeinstallprompt
    if (!banner) return;

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        const dismissed = localStorage.getItem('pwa_dismissed');
        if (!dismissed) {
            setTimeout(() => {
                banner.style.display = 'block';
                document.body.classList.add('pwa-banner-visible');
            }, 5000);
        }
    });

    if (installBtn) {
        installBtn.addEventListener('click', () => {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then(() => {
                deferredPrompt = null;
                hideBanner();
            });
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            localStorage.setItem('pwa_dismissed', '1');
            hideBanner();
        });
    }

    window.addEventListener('appinstalled', () => {
        hideBanner();
        deferredPrompt = null;
    });

    function hideBanner() {
        banner.style.display = 'none';
        document.body.classList.remove('pwa-banner-visible');
    }
})();
