# Plan d'implémentation - Tendereo Fixes

## Étape 1 : FIX CRITIQUE — Formulaire d'inscription (register.html)

**Fichier :** `app/templates/auth/register.html`
- Le champ `confirm_password` est ABSENT du template mais REQUIS par `RegisterForm` (forms.py:16-19) avec validator `EqualTo("password")`
- Le formulaire ne passe jamais la validation → "rien ne se passe"
- **Solution :** Ajouter le champ `confirm_password` + bouton œil toggle + erreurs affichées

**Changements :**
- Ajouter `<div class="form-group">` avec `form.confirm_password` et son toggle œil
- Ajouter `<span class="form-error">` pour afficher les erreurs de chaque champ
- Remplacer les styles inline par des classes CSS (auth-page, auth-container, auth-card, etc.)
- Ajouter bouton Google (placeholder pour étape 3)

## Étape 2 : SUPPRIMER système d'email vérification

**Fichiers à modifier :**

| Fichier | Action |
|---|---|
| `app/models.py:33-49` | Supprimer modèle `EmailVerification` |
| `app/services/__init__.py` | Vider le fichier, supprimer `generate_and_send_code` |
| `app/routes/auth.py:42-87` | Supprimer route `verify_email` |
| `app/routes/auth.py:115-133` | Supprimer route `admin_verify` |
| `app/routes/auth.py:136-171` | Simplifier `admin_register` (supprimer vérification email) |
| `app/routes/auth.py:174-212` | Simplifier `forgot_password` + `reset_password` (supprimer flow OTP) |
| `app/forms.py` | Supprimer `VerifyEmailForm`, `AdminVerifyForm` |
| `app/templates/auth/verify_email.html` | Supprimer |
| `app/templates/auth/admin_verify.html` | Supprimer |
| `app/__init__.py` | Supprimer Flask-Mail (init + import) |
| `requirements.txt` | Supprimer `Flask-Mail==0.10.0` |
| `config.py` | Supprimer MAIL_* configs |

**Note :** User créé directement avec `is_verified=True`. Pas de flow de vérification.

## Étape 3 : AJOUTER Google OAuth

**Fichiers à modifier :**

| Fichier | Action |
|---|---|
| `requirements.txt` | Ajouter `authlib` |
| `config.py` | Ajouter `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| `app/models.py` | Ajouter `google_id = db.Column(db.String(100), nullable=True, unique=True)` sur User |
| `app/routes/auth.py` | Ajouter routes `google_login` + `google_callback` |
| `app/templates/auth/register.html` | Bouton "S'inscrire avec Google" |
| `app/templates/auth/login.html` | Bouton "Se connecter avec Google" |
| Migration | Nouvelle migration pour `google_id` |

**Flow Google :**
1. Clic sur bouton Google → redirect vers Google OAuth
2. Google redirige vers `/auth/google/callback`
3. On récupère email, nom, google_id
4. Si user existe (par email ou google_id) → login
5. Si non → créer user avec google_id, password_hash vide, is_verified=True

## Étape 4 : FIX Dark Mode

**Fichiers :**
- `app/static/css/style.css` — Ajouter variables dark pour :
  - `.flash-success`, `.flash-error`, `.flash-info` (couleurs adaptatives)
  - `.form-error` (couleur adaptative)
  - `.auth-card` background
  - `.btn-google` colors
- `app/static/js/main.js:19` — Corriger `parentElement.textContent` qui écrase le bouton footer

**Avant (cassé) :**
```js
iconFooter.parentElement.textContent = theme === 'dark' ? ' Mode clair' : ' Mode sombre';
```

**Après (corrigé) :**
```js
const label = iconFooter.parentElement.querySelector('span') || iconFooter.nextSibling;
if (label && label.nodeType === 3) label.textContent = theme === 'dark' ? ' Mode clair' : ' Mode sombre';
```

## Étape 5 : FIX Responsive + Nettoyage styles inline

**Templates à nettoyer (remplacer styles inline par classes CSS) :**
- `app/templates/base.html` — navbar, footer, flash messages, PWA banner
- `app/templates/home/index.html` — hero, sections, grids
- `app/templates/auth/*.html` — formulaire layout (déjà fait étape 1)
- `app/templates/admin/dashboard.html` — grille responsive

**CSS à ajouter dans `style.css` :**
```css
/* Auth pages */
.auth-page { min-height: 80vh; display: flex; align-items: center; justify-content: center; background: var(--light-bg); }
.auth-container { max-width: 450px; width: 100%; padding: 0 1.5rem; }
.auth-header { text-align: center; margin-bottom: 2rem; }
.auth-logo { height: 60px; margin-bottom: 1rem; }
.auth-card { background: var(--white); padding: 2rem; border-radius: 16px; box-shadow: var(--shadow); }
.auth-footer { text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); }
.auth-footer a { color: var(--primary-teal); font-weight: 600; }
.auth-divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; color: var(--text-muted); font-size: 0.85rem; }
.auth-divider::before, .auth-divider::after { content: ''; flex: 1; border-bottom: 1px solid var(--border-color); }
.btn-google { width: 100%; justify-content: center; background: #fff; border: 1.5px solid var(--border-color); color: var(--text-dark); padding: 0.75rem; border-radius: 8px; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
.btn-google:hover { background: #f8f9fa; border-color: #ccc; }
.btn-full { width: 100%; justify-content: center; }
.form-error { color: #dc3545; font-size: 0.8rem; display: block; margin-top: 0.25rem; }
.password-wrapper { position: relative; }
.password-toggle { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: var(--text-muted); font-size: 1rem; }

/* Flash messages responsive */
.flash-close { background: none; border: none; float: right; cursor: pointer; font-size: 1.2rem; color: inherit; opacity: 0.7; }
.flash-close:hover { opacity: 1; }
```

**Dark mode additions :**
```css
[data-theme="dark"] .flash-success { background: rgba(21,87,36,0.3); color: #75e6a2; border-color: rgba(21,87,36,0.5); }
[data-theme="dark"] .flash-error { background: rgba(114,28,36,0.3); color: #f5a3aa; border-color: rgba(114,28,36,0.5); }
[data-theme="dark"] .flash-info { background: rgba(12,84,96,0.3); color: #8fd4e0; border-color: rgba(12,84,96,0.5); }
[data-theme="dark"] .form-error { color: #f5a3aa; }
[data-theme="dark"] .btn-google { background: var(--white); border-color: var(--border-color); color: var(--text-dark); }
[data-theme="dark"] .auth-card { background: var(--white); }
```

## Étape 6 : FIX Menu mobile + Flash messages

**Fichier : `app/static/js/main.js`**
- Ajouter fermeture menu mobile au clic sur un lien
- Ajouter fermeture au clic en dehors du menu
- Ajouter fermeture Escape
- Allonger flash duration à 8s + ajouter bouton fermer

## Étape 7 : FIX Cache/Rate-limit + Health check

**Fichier : `config.py`**
- `RATELIMIT_STORAGE_URI = "memory://"` reste pour dev, mais on note que Render free = 1 worker par défaut

**Fichier : `render.yaml`**
- Ajouter health check
- Garder `WEB_CONCURRENCY=1` (Render free ne supporte pas vraiment 4 workers)

**Fichier : `app/__init__.py`**
- Ajouter route `/health` → retourne `{"status": "ok"}`

## Étape 8 : NETTOYAGE

| Fichier | Action |
|---|---|
| `requirements.txt` | Supprimer `Flask-Admin==1.6.1`, `Pillow==11.1.0`, `Flask-Mail==0.10.0` |
| `app/routes/main.py:28` | Fixer `__import__("datetime")` → import en haut du fichier |
| `app/routes/auth.py:160-171` | Supprimer `admin_create_account` (route no-op) |
