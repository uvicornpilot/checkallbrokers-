//  Main JavaScript

// CKEditor context menu enhancement
function enhanceCKEditorContextMenu() {
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function(evt) {
            const editor = evt.editor;

            // Enhance context menu
            editor.on('contextMenu', function(evt) {
                const menu = evt.data.menu;
                if (menu) {
                    // Add custom styling
                    menu.element.addClass('enhanced-context-menu');
                }
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initModal();
    initForms();
    initSmoothScrolling();
    initPhoneInputs();
    initMobileMenu();
    initScrollAnimations();
    enhanceCKEditorContextMenu(); // Покращення контекстного меню CKEditor
    initExitIntent(); // Показ модалки при попытке уйти со страницы (без раннего интерстишла)
});

// Модальное окно
function initModal() {
    const modal = document.getElementById('consultationModal');
    // Прибираємо дублювання обробника подій - він буде в initForms()
}

function openConsultationForm() {
    const modal = document.getElementById('consultationModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        // Фокус на первое поле
        const firstInput = modal.querySelector('input');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

function closeConsultationForm() {
    const modal = document.getElementById('consultationModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';

        // Очистка формы
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

function showConsultationModal() {
    // Проверяем, не показывали ли уже модальное окно в этой сессии
    if (!sessionStorage.getItem('modalShown')) {
        openConsultationForm();
        sessionStorage.setItem('modalShown', 'true');
    }
}

// Закрытие модального окна при клике вне его
document.addEventListener('click', function(e) {
    const modal = document.getElementById('consultationModal');
    if (modal && e.target === modal) {
        closeConsultationForm();
    }
});

// Закрытие модального окна по Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeConsultationForm();
    }
});

// Формы
function initForms() {
    const consultationForms = document.querySelectorAll('#consultationFormComponent');
    consultationForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this, 'main');
        });
    });

    const modalForm = document.getElementById('modalConsultationForm');
    if (modalForm) {
        modalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this, 'modal');
        });
    }

    const sidebarForm = document.getElementById('sidebarConsultationForm');
    console.log('Sidebar form found:', sidebarForm); // Діагностика
    if (sidebarForm) {
        sidebarForm.addEventListener('submit', function(e) {
            console.log('Sidebar form submitted'); // Діагностика
            e.preventDefault();
            handleFormSubmission(this, 'sidebar');
        });
    } else {
        console.log('Sidebar form not found!'); // Діагностика
    }
}

function handleFormSubmission(form, type) {
    // Генеруємо унікальний ID для кожної відправки
    const submissionId = Date.now() + Math.random().toString(36).substr(2, 9);
    console.log(`Form submission started: ${type} (ID: ${submissionId})`); // Діагностика

    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    // Перевіряємо, чи форма вже відправляється
    if (form.dataset.submitting === 'true') {
        console.log(`Form ${type} is already submitting, ignoring duplicate submission`);
        return;
    }

    // Показываем состояние загрузки
    form.dataset.submitting = 'true';
    submitButton.disabled = true;
    submitButton.textContent = 'Отправка...';

    // Обрабатываем телефонные номера
    const phoneInput = form.querySelector('input[type="tel"]');
    if (phoneInput && phoneInput.iti) {
        const fullNumber = phoneInput.iti.getNumber();
        formData.set('phone', fullNumber);
        console.log('Phone number processed:', fullNumber); // Діагностика
    }

    // Валидация
    if (!validateForm(form)) {
        console.log('Form validation failed'); // Діагностика
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
    }

    console.log('Form validation passed'); // Діагностика

    // Определяем URL для отправки в зависимости от типа формы
    let submitUrl;
    if (type === 'modal') {
        submitUrl = '/consultations/modal-submit/';
    } else if (type === 'sidebar') {
        submitUrl = '/consultations/submit-ajax/';
    } else {
        submitUrl = '/consultations/submit-ajax/';
    }

    // Отправка формы
    console.log('Sending form to URL:', submitUrl); // Діагностика
    console.log('Form data:', Object.fromEntries(formData)); // Діагностика

    fetch(submitUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(form)
        }
    })
    .then(response => {
        console.log('Response status:', response.status); // Діагностика
        console.log('Response headers:', response.headers); // Діагностика
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data); // Діагностика
        if (data.success) {
            if (type === 'modal') {
                // Для модального вікна показываем ответ внутри модального окна
                showModalResponse(data.message || 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время..');
                form.reset();
            } else {
                // Для других форм показываем обычное сообщение
                showMessage(form, 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время..', 'success');
                form.reset();
            }
        } else {
            showMessage(form, data.message || 'Произошла ошибка при отправке заявки. Попробуйте еще раз.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage(form, 'Произошла ошибка при отправке заявки. Попробуйте еще раз.', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        form.dataset.submitting = 'false'; // Скидаємо флаг відправки
    });
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    // Удаляем предыдущие сообщения об ошибках
    form.querySelectorAll('.form-group__error, .sidebar-form__error').forEach(error => error.remove());
    form.querySelectorAll('.form-group__input--error, .sidebar-form__input--error').forEach(input => {
        input.classList.remove('form-group__input--error', 'sidebar-form__input--error');
    });

    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'Это поле обязательно для заполнения');
            isValid = false;
        } else if (input.type === 'tel' && !validatePhone(input.value, input)) {
            showFieldError(input, 'Введите корректный номер телефона');
            isValid = false;
        } else if (input.type === 'email' && !validateEmail(input.value)) {
            showFieldError(input, 'Введите корректный email');
            isValid = false;
        }
    });

    return isValid;
}

function validatePhone(phone, input) {
    // Без проверки формата/длины — просто убеждаемся, что есть цифры
    const digitsOnly = (phone || '').replace(/\D/g, '');
    return digitsOnly.length >= 5;
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(input, message) {
    // Добавляем класс ошибки в зависимости от типа формы
    if (input.closest('.sidebar-form__form')) {
        input.classList.add('sidebar-form__input--error');
    } else {
        input.classList.add('form-group__input--error');
    }

    const errorElement = document.createElement('div');
    errorElement.className = input.closest('.sidebar-form__form') ? 'sidebar-form__error' : 'form-group__error';
    errorElement.textContent = message;

    const formGroup = input.closest('.form-group, .form-field');
    if (formGroup) {
        formGroup.appendChild(errorElement);
    }
}

function showMessage(form, message, type) {
    // Удаляем предыдущие сообщения
    form.querySelectorAll('.form-message, .sidebar-form__message').forEach(msg => msg.remove());

    const messageElement = document.createElement('div');

    // Специальная обработка для sidebar формы
    if (form.classList.contains('sidebar-form__form')) {
        messageElement.className = `sidebar-form__message sidebar-form__message--${type}`;
    } else {
        messageElement.className = `form-message form-message--${type}`;
    }

    messageElement.textContent = message;

    form.appendChild(messageElement);

    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}

function showModalResponse(message) {
    const modal = document.getElementById('consultationModal');
    if (modal) {
        // Очищаем содержимое модального окна
        const modalContent = modal.querySelector('.modal__content');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="modal__response">

                    <h2 class="modal__response-title">Спасибо!</h2>
                    <p class="modal__response-message">${message}</p>
                    <button class="btn btn--primary" onclick="closeConsultationForm()">Закрыть</button>
                </div>
            `;
        }
    }
}

function getCSRFToken(form) {
    const token = form
        ? form.querySelector('input[name="csrfmiddlewaretoken"]')
        : document.querySelector('input[name="csrfmiddlewaretoken"]');
    console.log('CSRF token found:', token ? token.value : 'NOT FOUND'); // Діагностика
    return token ? token.value : '';
}

// Плавная прокрутка
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                const headerHeight = document.querySelector('.header')?.offsetHeight || 0;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initPhoneInputs() {
    const phoneInputs = document.querySelectorAll('.intl-tel-input');
    console.log('Found phone inputs:', phoneInputs.length); // Діагностика

    // Ждём, пока загрузятся и intlTelInput, и geo-phone.js (createPhoneInput)
    if (phoneInputs.length > 0 && (typeof window.intlTelInput !== 'function' || typeof window.createPhoneInput !== 'function')) {
        console.warn('intlTelInput/geo-phone not loaded yet; deferring phone inputs init until window.load');
        window.addEventListener('load', initPhoneInputs, { once: true });
        return;
    }

    phoneInputs.forEach((input, index) => {
        console.log(`Initializing phone input ${index + 1}:`, input.id || input.name); // Діагностика

        if (typeof window.createPhoneInput === 'function') {
            // Инициализируем через geo-phone.js (5 сервисов geo-детекта + кэш в sessionStorage)
            const iti = window.createPhoneInput(input, {
                preferredCountries: ['us', 'ua', 'pl', 'by', 'kz', 'de', 'gb', 'ru'],
            });

            if (iti) {
                // Добавляем валидацию при вводе
                input.addEventListener('blur', function() {
                    if (iti.isValidNumber()) {
                        input.classList.remove('form-group__input--error');
                        input.classList.add('form-group__input--valid');
                    } else {
                        input.classList.remove('form-group__input--valid');
                        input.classList.add('form-group__input--error');
                    }
                });

                // Сохраняем экземпляр для использования в валидации
                input.iti = iti;
                console.log(`Phone input ${index + 1} initialized successfully`); // Діагностика
            }
        } else {
            console.warn('createPhoneInput (geo-phone.js) is unavailable; skipping this input for now');
        }
    });
}
// Mobile Menu Toggle
function toggleMobileMenu() {
    const nav = document.getElementById('mainNav');
    const toggle = document.querySelector('.mobile-menu-toggle');

    if (nav && toggle) {
        nav.classList.toggle('nav--open');
        toggle.classList.toggle('mobile-menu-toggle--active');

        // Prevent body scroll when menu is open
        if (nav.classList.contains('nav--open')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}


// Chat Widget Functions
function openChat() {
    const chatWidget = document.getElementById('chatWidget');
    if (chatWidget) {
        chatWidget.classList.add('chat-widget--open');
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.focus();
        }
    }
}

function closeChat() {
    const chatWidget = document.getElementById('chatWidget');
    if (chatWidget) {
        chatWidget.classList.remove('chat-widget--open');
    }
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (message) {
        addChatMessage(message, 'user');
        input.value = '';

        // Simulate bot response
        setTimeout(() => {
            const botResponses = [
                "Спасибо за ваше сообщение! Для получения детальной консультации, пожалуйста, заполните форму заявки.",
                "Понял ваш вопрос! Чтобы наш специалист мог помочь вам, заполните форму заявки.",
                "Отличный вопрос! Для решения вашей проблемы заполните форму заявки на бесплатную консультацию.",
                "Спасибо! Для получения профессиональной помощи заполните форму заявки."
            ];

            const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)];
            addChatMessage(randomResponse, 'bot');

            // Show form button after bot response
            setTimeout(() => {
                addChatFormButton();
            }, 500);
        }, 1000);
    }
}

function addChatFormButton() {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
        const formButtonDiv = document.createElement('div');
        formButtonDiv.className = 'chat-message chat-message--bot';
        formButtonDiv.innerHTML = `
            <div class="chat-message__content">
                <button class="chat-form-btn" onclick="openConsultationFormFromChat()">
                    📝 Заполнить форму заявки
                </button>
            </div>
        `;

        messagesContainer.appendChild(formButtonDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function openConsultationFormFromChat() {
    closeChat();
    openConsultationForm();
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function addChatMessage(text, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    if (messagesContainer) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message chat-message--${sender}`;

        const now = new Date();
        const timeString = now.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="chat-message__content">
                <p>${text}</p>
            </div>
            <div class="chat-message__time">${timeString}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Мобильное меню
function initMobileMenu() {
    const nav = document.getElementById('mainNav');
    const toggle = document.querySelector('.mobile-menu-toggle');
    const overlay = document.querySelector('.nav__overlay');

    // Тихо пропускаємо ініціалізацію, якщо елементи відсутні на поточній сторінці
    if (!(nav && toggle)) {
        return;
    }

    if (nav && toggle) {
        // Обработчик клика
        toggle.addEventListener('click', function() {
            toggleMobileMenu();
        });

        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (nav.classList.contains('nav--open') &&
                !nav.contains(e.target) &&
                !toggle.contains(e.target) &&
                !(overlay && overlay.contains(e.target))) {
                toggleMobileMenu();
            }
        });

        // Закрытие меню при клике на ссылку
        const navLinks = nav.querySelectorAll('.nav__link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (nav.classList.contains('nav--open')) {
                    toggleMobileMenu();
                }
            });
        });
    }
}

// Анимации при скролле
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами, которые нужно анимировать
    const animatedElements = document.querySelectorAll('.service-card, .blog-card, .blog-post');
    animatedElements.forEach(el => observer.observe(el));
}

// Инициализация анимаций при загрузке
window.addEventListener('load', function() {
    initScrollAnimations();
});

// Утилиты
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Обработка изменения размера окна
window.addEventListener('resize', debounce(function() {
    // Пересчитываем позиции для мобильного меню
    const navList = document.querySelector('.nav__list');
    if (navList && window.innerWidth > 768) {
        navList.classList.remove('nav__list--open');
        const mobileToggle = document.querySelector('.nav__mobile-toggle');
        if (mobileToggle) {
            mobileToggle.classList.remove('nav__mobile-toggle--active');
        }
    }
}, 250));

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('consultationModal');
    if (event.target === modal) {
        closeConsultationForm();
    }
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <div class="notification__content">
            <span class="notification__message">${message}</span>
            <button class="notification__close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Add notification styles dynamically
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    }

    .notification--success {
        border-left: 4px solid var(--primary-color);
    }

    .notification--error {
        border-left: 4px solid #e74c3c;
    }

    .notification--info {
        border-left: 4px solid #3498db;
    }

    .notification__content {
        padding: 15px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
    }

    .notification__message {
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.4;
    }

    .notification__close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #999;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .notification__close:hover {
        color: var(--text-primary);
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Глобальные функции для использования в HTML
window.openConsultationForm = openConsultationForm;
window.closeConsultationForm = closeConsultationForm;
window.toggleMobileMenu = toggleMobileMenu;
window.openChat = openChat;
window.closeChat = closeChat;
window.sendChatMessage = sendChatMessage;
window.handleChatKeyPress = handleChatKeyPress;
window.openConsultationFormFromChat = openConsultationFormFromChat;

// Обробка відправки відгуку
function handleReviewSubmission(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('.review-form__submit');
    const originalText = submitButton.textContent;

    // Показуємо стан завантаження
    submitButton.disabled = true;
    submitButton.textContent = 'Отправка...';

    // Валідація
    if (!validateReviewForm(form)) {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
    }

    // Відправка форми
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showReviewMessage(form, data.message, 'success');
            form.reset();
        } else {
            showReviewErrors(form, data.errors);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showReviewMessage(form, 'Произошла ошибка при отправке отзыва. Попробуйте еще раз.', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        form.dataset.submitting = 'false'; // Скидаємо флаг відправки
    });
}

// Валідація форми відгуку
function validateReviewForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    // Видаляємо попередні повідомлення про помилки
    form.querySelectorAll('.review-form__error').forEach(error => error.remove());
    form.querySelectorAll('.review-form__input--error, .review-form__textarea--error, .review-form__select--error').forEach(input => {
        input.classList.remove('review-form__input--error', 'review-form__textarea--error', 'review-form__select--error');
    });

    inputs.forEach(input => {
        if (!input.value.trim()) {
            showReviewFieldError(input, 'Это поле обязательно для заполнения');
            isValid = false;
        }
    });

    return isValid;
}

// Показати помилку поля відгуку
function showReviewFieldError(input, message) {
    input.classList.add('review-form__input--error', 'review-form__textarea--error', 'review-form__select--error');

    const errorElement = document.createElement('div');
    errorElement.className = 'review-form__error';
    errorElement.textContent = message;

    const field = input.closest('.review-form__field');
    if (field) {
        field.appendChild(errorElement);
    }
}

// Показати повідомлення відгуку
function showReviewMessage(form, message, type) {
    // Видаляємо попередні повідомлення
    form.querySelectorAll('.review-form__message').forEach(msg => msg.remove());

    const messageElement = document.createElement('div');
    messageElement.className = `review-form__message review-form__message--${type}`;
    messageElement.textContent = message;

    form.appendChild(messageElement);

    // Автоматично приховуємо повідомлення через 5 секунд
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}

// Показати помилки відгуку
function showReviewErrors(form, errors) {
    Object.keys(errors).forEach(fieldName => {
        const input = form.querySelector(`[name="${fieldName}"]`);
        if (input) {
            showReviewFieldError(input, errors[fieldName][0]);
        }
    });
}

// --- NEW MOBILE NAVIGATION ---
document.addEventListener('DOMContentLoaded', function () {
    const burger = document.getElementById('burgerBtn');
    const nav = document.getElementById('mobileNav');
    const closeBtn = document.getElementById('closeNavBtn');
    const overlay = document.getElementById('mobileNavOverlay');

    function openMenu() {
        nav.classList.add('open');
        overlay.classList.add('open');
        document.body.classList.add('mobile-nav-open');
    }
    function closeMenu() {
        nav.classList.remove('open');
        overlay.classList.remove('open');
        document.body.classList.remove('mobile-nav-open');
    }
    if (burger) {
        burger.addEventListener('click', openMenu);
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }
    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }
    // Закривати меню при переході по пункту
    document.querySelectorAll('.mobile-nav__list a').forEach(function(link) {
        link.addEventListener('click', closeMenu);
    });
});

// ==== Блог: защита контента статьи (копирование/правый клик) ====
document.addEventListener("DOMContentLoaded", function () {
    var articleContainer = document.querySelector(".blog-detail");
    if (!articleContainer) return;

    if (articleContainer.dataset.disableCopy === "true") {
        document.addEventListener("copy", function (e) {
            e.preventDefault();
        });
        document.addEventListener("keydown", function (e) {
            var key = (e.key || '').toLowerCase();
            if ((e.ctrlKey || e.metaKey) && ["c", "u", "s"].includes(key)) {
                e.preventDefault();
            }
        });
    }

    if (articleContainer.dataset.disableRightClick === "true") {
        document.addEventListener("contextmenu", function (e) {
            e.preventDefault();
        });
    }
});

// === Reviews / Comments: ответ на комментарий (единственная логика, форма НЕ двигается по DOM) ===
document.addEventListener('DOMContentLoaded', function () {
    const reviewsSection = document.getElementById('reviews');
    if (!reviewsSection) return; // на странице нет блока отзывов — ничего не делаем

    const parentInput = document.getElementById('id_parent');
    const indicator = document.getElementById('reviewReplyingIndicator');
    const indicatorText = document.getElementById('reviewReplyingText');
    const cancelBtn = document.getElementById('cancelReplyBtn');
    const formSection = document.getElementById('reviewFormHome');
    const formTitle = document.getElementById('reviewFormTitle');
    const reviewForm = document.getElementById('reviewForm');

    // AJAX-отправка формы отзыва
    if (reviewForm) {
        reviewForm.addEventListener('submit', function (e) {
            e.preventDefault();
            handleReviewSubmission(this);
        });
    }

    function scrollToReviewForm() {
        formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    reviewsSection.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-reply-to]');
        if (!btn) return;

        parentInput.value = btn.getAttribute('data-reply-to');
        indicator.style.display = 'flex';
        indicatorText.textContent = 'Вы отвечаете: ' + btn.getAttribute('data-reply-name');
        formTitle.textContent = 'Ваш ответ';

        scrollToReviewForm();
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function () {
            parentInput.value = '';
            indicator.style.display = 'none';
            formTitle.textContent = 'Оставить отзыв';
        });
    }
});

// === Exit-intent: mouseleave (desktop) + скролл 60% (mobile) + таймер 25 сек как гарантированный fallback ===
// Работает только на статьях из категорий: obzor-brokerov, proverennyye-birzhi-white-list, preduprezhdeniya-i-skam-black-list
function initExitIntent() {
    const ALLOWED_CATEGORIES = ['obzor-brokerov', 'proverennyye-birzhi-white-list', 'preduprezhdeniya-i-skam-black-list'];

    const articleEl = document.querySelector('.blog-detail');
    const categorySlug = articleEl ? articleEl.dataset.categorySlug : null;

    if (!ALLOWED_CATEGORIES.includes(categorySlug)) {
        return;
    }

    if (sessionStorage.getItem('modalShown')) {
        return;
    }

    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    // --- Desktop: курсор уходит за верх окна ---
    if (!isMobile) {
        document.addEventListener('mouseleave', function (e) {
            if (e.clientY <= 0) {
                showConsultationModal();
            }
        });
    }

    // --- Mobile: скролл 60%+ страницы ---
    if (isMobile) {
        window.addEventListener('scroll', function () {
            if (sessionStorage.getItem('modalShown')) return;

            const scrolled = window.scrollY + window.innerHeight;
            const total = document.documentElement.scrollHeight;
            const percent = (scrolled / total) * 100;

            if (percent >= 60) {
                showConsultationModal();
            }
        }, { passive: true });
    }

    // --- Fallback: гарантированный показ через 25 секунд, если ничего выше не сработало ---
    setTimeout(function () {
        showConsultationModal();
    }, 25000);
}

// === FAQ: аккордеон ===
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.faq-question').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const item = btn.closest('.faq-item');
            const answer = item.querySelector('.faq-answer');
            const isOpen = item.classList.contains('is-open');

            if (isOpen) {
                answer.style.maxHeight = null;
                item.classList.remove('is-open');
                btn.setAttribute('aria-expanded', 'false');
            } else {
                answer.style.maxHeight = answer.scrollHeight + 'px';
                item.classList.add('is-open');
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });
});