// =====================================================
// geo-phone.js — общий модуль
// Подключать ПЕРВЫМ из ваших JS файлов
// =====================================================

// ── Определение страны по IP ──────────────────────
// Все запросы делаются из браузера клиента.
// Nginx не влияет — он не участвует в этих запросах.
// 5 сервисов по очереди, таймаут 3 сек на каждый.
// Результат кэшируется в sessionStorage.

window.detectCountryCode = async function () {
    const cached = sessionStorage.getItem('_geo_country');
    if (cached) return cached;

    const services = [
        async () => {
            const r = await fetch('https://api.country.is/', { signal: AbortSignal.timeout(3000) });
            const d = await r.json();
            if (d && d.country) return d.country.toUpperCase();
        },
        async () => {
            const r = await fetch('https://ipapi.co/json/', { signal: AbortSignal.timeout(3000) });
            const d = await r.json();
            if (d && d.country_code) return d.country_code.toUpperCase();
        },
        async () => {
            const r = await fetch('https://freeipapi.com/api/json', { signal: AbortSignal.timeout(3000) });
            const d = await r.json();
            if (d && d.countryCode) return d.countryCode.toUpperCase();
        },
        async () => {
            const r = await fetch('https://ip-api.com/json/?fields=countryCode', { signal: AbortSignal.timeout(3000) });
            const d = await r.json();
            if (d && d.countryCode) return d.countryCode.toUpperCase();
        },
        async () => {
            const r = await fetch('https://ipinfo.io/json', { signal: AbortSignal.timeout(3000) });
            const d = await r.json();
            if (d && d.country) return d.country.toUpperCase();
        },
    ];

    for (const service of services) {
        try {
            const code = await service();
            if (code && /^[A-Z]{2}$/.test(code)) {
                sessionStorage.setItem('_geo_country', code);
                console.log('🌍 Страна определена:', code);
                return code;
            }
        } catch (e) {
            // тихо пробуем следующий сервис
        }
    }

    console.warn('⚠️ Страна не определена, используем US');
    return 'US';
};

// ── Инициализация intl-tel-input ──────────────────
// Показывает US сразу, потом асинхронно ставит реальную страну.
// Пользователь не ждёт загрузки geo.

window.createPhoneInput = function (inputEl, extraOptions) {
    if (!inputEl) {
        console.error('createPhoneInput: элемент не найден');
        return null;
    }
    if (!window.intlTelInput) {
        console.error('createPhoneInput: intlTelInput не загружен');
        return null;
    }

    const options = Object.assign({
        initialCountry: 'us',
        separateDialCode: true,
        autoPlaceholder: 'aggressive',
        nationalMode: false,
        dropdownContainer: document.body,
        preferredCountries: ['us', 'ua', 'pl', 'by', 'kz', 'de', 'gb', 'ru'],
        utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js',
    }, extraOptions || {});

    const iti = window.intlTelInput(inputEl, options);

    // Асинхронно подгружаем реальную страну
    window.detectCountryCode().then(function (code) {
        try {
            iti.setCountry(code.toLowerCase());
        } catch (e) {
            console.warn('Не удалось установить страну:', code);
        }
    });

    return iti;
};

// ── Валидация телефона ────────────────────────────

window.validatePhone = function (iti) {
    if (!iti) return false;
    try {
        // isValidNumber() — из utils.js (google-libphonenumber)
        return iti.isValidNumber();
    } catch (e) {
        // utils ещё не загружен — fallback на длину цифр
        return iti.getNumber().replace(/\D/g, '').length >= 7;
    }
};

// ── UI утилиты (используются в обеих формах) ─────

// Показывает ошибку под полем (без alert)
window.showFieldError = function (field, message) {
    if (!field) return;
    field.classList.add('input-error');
    var hint = field.nextElementSibling;
    if (!hint || !hint.classList.contains('_field-hint')) {
        hint = document.createElement('span');
        hint.className = '_field-hint';
        field.parentNode.insertBefore(hint, field.nextSibling);
    }
    hint.textContent = message;
    hint.style.cssText = 'display:block;color:#e53e3e;font-size:12px;margin-top:4px;';
    field.focus();
};

window.clearFieldError = function (field) {
    if (!field) return;
    field.classList.remove('input-error');
    var hint = field.nextElementSibling;
    if (hint && hint.classList.contains('_field-hint')) hint.remove();
};

// Тост вместо alert
window.showToast = function (message, type) {
    type = type || 'info';
    var toast = document.getElementById('_global_toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = '_global_toast';
        toast.style.cssText = [
            'position:fixed;bottom:24px;right:24px;z-index:99999;',
            'padding:14px 20px;border-radius:8px;font-size:14px;',
            'max-width:340px;box-shadow:0 4px 20px rgba(0,0,0,.18);',
            'transition:opacity .3s;font-family:inherit;color:#fff;',
        ].join('');
        document.body.appendChild(toast);
    }
    var colors = { error: '#e53e3e', success: '#38a169', warning: '#d69e2e', info: '#3182ce' };
    toast.style.background = colors[type] || colors.info;
    toast.style.opacity = '1';
    toast.textContent = message;
    clearTimeout(toast._timer);
    toast._timer = setTimeout(function () { toast.style.opacity = '0'; }, 4000);
};

// Читает CSRF-токен Django из cookie
window.getCsrfToken = function () {
    var match = document.cookie.match(/(?:^|; )csrftoken=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : '';
};