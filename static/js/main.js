// Broker Control - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initModal();
    initForms();
    initSmoothScrolling();
    
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
    const consultationForm = document.getElementById('consultationForm');
    if (consultationForm) {
        consultationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this, 'main');
        });
    }
}

function handleFormSubmission(form, type) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Показываем состояние загрузки
    submitButton.disabled = true;
    submitButton.textContent = 'Отправка...';
    
    // Валидация
    if (!validateForm(form)) {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        return;
    }
    
    // Отправка формы
    fetch('/consultations/submit/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(form, 'Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в течение 24 часов.', 'success');
            form.reset();
            
            // Закрываем модальное окно, если это оно
            if (type === 'modal') {
                closeConsultationForm();
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
    form.querySelectorAll('.form-group__error').forEach(error => error.remove());
    form.querySelectorAll('.form-group__input--error').forEach(input => {
        input.classList.remove('form-group__input--error');
    });
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'Это поле обязательно для заполнения');
            isValid = false;
        } else if (input.type === 'tel' && !validatePhone(input.value)) {
            showFieldError(input, 'Введите корректный номер телефона');
            isValid = false;
        } else if (input.type === 'email' && !validateEmail(input.value)) {
            showFieldError(input, 'Введите корректный email');
            isValid = false;
        }
    });
    
    return isValid;
}

function validatePhone(phone) {
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(input, message) {
    input.classList.add('form-group__input--error');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'form-group__error';
    errorElement.textContent = message;
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(errorElement);
    }
}

function showMessage(form, message, type) {
    // Удаляем предыдущие сообщения
    form.querySelectorAll('.form-message').forEach(msg => msg.remove());
    
    const messageElement = document.createElement('div');
    messageElement.className = `form-message form-message--${type}`;
    messageElement.textContent = message;
    
    form.appendChild(messageElement);
    
    // Автоматически скрываем сообщение через 5 секунд
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
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