// Main JavaScript file for Broker Control
// Compatible with future Django + Vue.js integration

class BrokerControl {
    constructor() {
        this.modal = null;
        this.forms = [];
        this.init();
    }

    init() {
        this.initModal();
        this.initForms();
        this.initScrollEffects();
        this.initAutoPopup();
        this.initSmoothScrolling();
    }

    // Initialize modal functionality
    initModal() {
        this.modal = document.getElementById('modal');
        
        // Close modal when clicking outside
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display === 'block') {
                this.closeModal();
            }
        });
    }

    // Initialize form handling
    initForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach((form, index) => {
            this.forms.push(form);
            
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit(form, index);
            });

            // Add input validation
            const inputs = form.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateInput(input));
                input.addEventListener('input', () => this.clearInputError(input));
            });
        });
    }

    // Initialize scroll effects
    initScrollEffects() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.service-card, .blog-card, .about-content');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    // Initialize auto popup after 3 seconds
    initAutoPopup() {
        setTimeout(() => {
            this.openModal();
        }, 3000);
    }

    // Initialize smooth scrolling for anchor links
    initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Open modal
    openModal() {
        if (this.modal) {
            this.modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            // Focus first input in modal
            const firstInput = this.modal.querySelector('input');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    // Close modal
    closeModal() {
        if (this.modal) {
            this.modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            
            // Reset modal form
            const modalForm = this.modal.querySelector('form');
            if (modalForm) {
                modalForm.reset();
                this.clearFormErrors(modalForm);
            }
        }
    }

    // Handle form submission
    async handleFormSubmit(form, formIndex) {
        if (!this.validateForm(form)) {
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Надсилання...';

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Simulate API call (replace with actual endpoint in Django)
            await this.simulateApiCall(data);
            
            // Show success message
            this.showSuccessMessage(form, 'Дякуємо! Ваша заявка успішно надіслана. Ми зв\'яжемося з вами найближчим часом.');
            
            // Reset form
            form.reset();
            this.clearFormErrors(form);
            
            // Close modal if it's the modal form
            if (form.closest('#modal')) {
                this.closeModal();
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showErrorMessage(form, 'Помилка при надсиланні заявки. Спробуйте ще раз.');
        } finally {
            // Restore button state
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    // Validate form
    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    // Validate individual input
    validateInput(input) {
        const value = input.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Clear previous error
        this.clearInputError(input);

        // Check if required field is empty
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Це поле обов\'язкове для заповнення';
        }

        // Validate email
        if (input.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Введіть коректну email адресу';
            }
        }

        // Validate phone
        if (input.type === 'tel' && value) {
            const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
            if (!phoneRegex.test(value)) {
                isValid = false;
                errorMessage = 'Введіть коректний номер телефону';
            }
        }

        // Show error if validation failed
        if (!isValid) {
            this.showInputError(input, errorMessage);
        }

        return isValid;
    }

    // Show input error
    showInputError(input, message) {
        input.classList.add('form-group__input--error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-group__error';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
    }

    // Clear input error
    clearInputError(input) {
        input.classList.remove('form-group__input--error');
        const errorDiv = input.parentNode.querySelector('.form-group__error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Clear all form errors
    clearFormErrors(form) {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => this.clearInputError(input));
    }

    // Show success message
    showSuccessMessage(form, message) {
        this.showMessage(form, message, 'success');
    }

    // Show error message
    showErrorMessage(form, message) {
        this.showMessage(form, message, 'error');
    }

    // Show message
    showMessage(form, message, type) {
        // Remove existing messages
        const existingMessage = form.querySelector('.form-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `form-message form-message--${type}`;
        messageDiv.textContent = message;

        form.appendChild(messageDiv);

        // Auto-remove message after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // Simulate API call (replace with actual Django endpoint)
    async simulateApiCall(data) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate 90% success rate
                if (Math.random() > 0.1) {
                    resolve({ success: true, message: 'Form submitted successfully' });
                } else {
                    reject(new Error('Network error'));
                }
            }, 1000);
        });
    }

    // Analytics tracking (for future integration)
    trackEvent(eventName, data = {}) {
        // Placeholder for analytics integration
        console.log('Analytics event:', eventName, data);
        
        // Future integration with Google Analytics, Yandex.Metrica, etc.
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, data);
        }
    }

    // SEO-friendly URL handling
    handleUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const action = urlParams.get('action');
        
        if (action === 'consult') {
            this.openModal();
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.brokerControl = new BrokerControl();
    
    // Handle URL parameters
    window.brokerControl.handleUrlParams();
});

// Global functions for HTML onclick handlers
function openConsultationForm() {
    if (window.brokerControl) {
        window.brokerControl.openModal();
        window.brokerControl.trackEvent('consultation_form_opened');
    }
}

function closeModal() {
    if (window.brokerControl) {
        window.brokerControl.closeModal();
    }
}

// Export for future Vue.js integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BrokerControl;
}

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    // Future integration with error tracking services
});

// Performance monitoring
window.addEventListener('load', () => {
    // Track page load performance
    if ('performance' in window) {
        const perfData = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart);
    }
}); 