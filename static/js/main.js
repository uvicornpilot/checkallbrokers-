// Broker Control - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initModal();
    initForms();
    initSmoothScrolling();
    initPhoneInputs();
    
    // Показ модального окна через 3 секунды
    setTimeout(function() {
        showConsultationModal();
    }, 3000);
});

// Модальное окно
function initModal() {
    const modal = document.getElementById('consultationModal');
    const modalForm = document.getElementById('modalConsultationForm');
    
    if (modalForm) {
        modalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this, 'modal');
        });
    }
    
    // Завантажуємо налаштування для модального вікна
    loadModalFormSettings();
}

function loadModalFormSettings() {
    fetch('/consultations/settings/')
        .then(response => response.json())
        .then(data => {
            // Показуємо/приховуємо поля згідно з налаштуваннями
            if (data.show_email_field) {
                const emailField = document.getElementById('modalEmailField');
                if (emailField) emailField.style.display = 'block';
            }
            if (data.show_broker_field) {
                const brokerField = document.getElementById('modalBrokerField');
                if (brokerField) brokerField.style.display = 'block';
            }
            if (data.show_amount_field) {
                const amountField = document.getElementById('modalAmountField');
                if (amountField) amountField.style.display = 'block';
            }
            if (data.show_investment_type_field) {
                const investmentField = document.getElementById('modalInvestmentField');
                if (investmentField) investmentField.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Помилка завантаження налаштувань модального вікна:', error);
        });
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
    console.log('Form submission started:', type); // Діагностика
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Показываем состояние загрузки
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
    
    // Визначаємо URL для відправки форми
    let submitUrl;
    if (type === 'modal') {
        submitUrl = '/consultations/modal-submit/';
    } else if (type === 'sidebar') {
        submitUrl = '/consultations/submit-ajax/';
    } else {
        submitUrl = '/consultations/submit-ajax/';
    }
    
    // Отправка формы
    fetch(submitUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (type === 'modal') {
                // Для модального вікна показываем ответ внутри модального окна
                showModalResponse(data.message || 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.');
                form.reset();
            } else {
                // Для других форм показываем обычное сообщение
                showMessage(form, 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.', 'success');
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
    // Если есть intl-tel-input, используем его валидацию
    if (input && input.iti) {
        return input.iti.isValidNumber();
    }
    
    // Fallback валидация
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
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
                    <div class="modal__response-icon">✅</div>
                    <h2 class="modal__response-title">Спасибо!</h2>
                    <p class="modal__response-message">${message}</p>
                    <button class="btn btn--primary" onclick="closeConsultationForm()">Закрыть</button>
                </div>
            `;
        }
    }
}

function getCSRFToken() {
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]');
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

// Инициализация телефонных полей
function initPhoneInputs() {
    const phoneInputs = document.querySelectorAll('.intl-tel-input');
    console.log('Found phone inputs:', phoneInputs.length); // Діагностика
    
    phoneInputs.forEach((input, index) => {
        console.log(`Initializing phone input ${index + 1}:`, input.id || input.name); // Діагностика
        
        // Инициализируем intl-tel-input
        const iti = window.intlTelInput(input, {
            initialCountry: 'auto',
            geoIpLookup: function(callback) {
                fetch('https://ipapi.co/json')
                    .then(res => res.json())
                    .then(data => callback(data.country_code))
                    .catch(() => callback('ua')); // По умолчанию Украина
            },
            preferredCountries: ['ua', 'ru', 'kz', 'by'],
            separateDialCode: true,
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
        });
        
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
    
    if (nav && toggle) {
        // Обработчик клика
        toggle.addEventListener('click', function() {
            toggleMobileMenu();
        });
        
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (nav.classList.contains('nav--open') && 
                !nav.contains(e.target) && 
                !toggle.contains(e.target)) {
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

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

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