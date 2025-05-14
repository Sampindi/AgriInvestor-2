// Main JavaScript file for AgriConnect

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (navbarToggler && navbarNav) {
        navbarToggler.addEventListener('click', function() {
            navbarNav.classList.toggle('show');
        });
    }
    
    // Project image gallery (for project detail page)
    const mainImage = document.querySelector('.project-main-image');
    const thumbnails = document.querySelectorAll('.project-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Update main image source
                mainImage.src = this.src;
                
                // Update active thumbnail
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
    
    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    
    if (progressBars.length > 0) {
        progressBars.forEach(progressBar => {
            const width = progressBar.getAttribute('data-width');
            progressBar.style.width = '0%';
            
            // Use setTimeout to ensure the initial width is applied before animation
            setTimeout(() => {
                progressBar.style.width = width + '%';
            }, 100);
        });
    }
    
    // Form validation highlights
    const forms = document.querySelectorAll('form');
    
    if (forms.length > 0) {
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Add validation classes on blur
                input.addEventListener('blur', function() {
                    if (this.value.trim() === '' && this.hasAttribute('required')) {
                        this.classList.add('is-invalid');
                        this.classList.remove('is-valid');
                    } else {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                    }
                });
                
                // Reset validation on focus
                input.addEventListener('focus', function() {
                    this.classList.remove('is-invalid');
                });
            });
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.transition = 'opacity 1s ease-out';
                message.style.opacity = '0';
                
                setTimeout(() => {
                    message.remove();
                }, 1000);
            }, 5000);
        });
    }
    
    // Profile tabs functionality
    const profileTabs = document.querySelectorAll('.profile-tab');
    const profileTabContents = document.querySelectorAll('.profile-tab-content');
    
    if (profileTabs.length > 0 && profileTabContents.length > 0) {
        profileTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Update active tab
                profileTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding content
                const tabId = this.getAttribute('data-tab');
                profileTabContents.forEach(content => {
                    content.style.display = 'none';
                });
                
                document.getElementById(tabId).style.display = 'block';
            });
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    if (anchorLinks.length > 0) {
        anchorLinks.forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80, // Offset for fixed header
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // Animated counters (for statistics)
    const counters = document.querySelectorAll('.counter');
    
    if (counters.length > 0) {
        const isElementInViewport = (el) => {
            const rect = el.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        };
        
        const animateCounter = (counter) => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                counter.textContent = Math.floor(current);
                
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                }
            }, 16);
        };
        
        const checkCounters = () => {
            counters.forEach(counter => {
                if (isElementInViewport(counter) && !counter.classList.contains('counted')) {
                    counter.classList.add('counted');
                    animateCounter(counter);
                }
            });
        };
        
        // Initial check
        checkCounters();
        
        // Check on scroll
        window.addEventListener('scroll', checkCounters);
    }
    
    // Form character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    if (textareas.length > 0) {
        textareas.forEach(textarea => {
            const maxLength = textarea.getAttribute('maxlength');
            const counterElement = document.createElement('div');
            counterElement.className = 'text-secondary mt-1 small';
            counterElement.textContent = `0/${maxLength} characters`;
            
            textarea.parentNode.insertBefore(counterElement, textarea.nextSibling);
            
            textarea.addEventListener('input', function() {
                const currentLength = this.value.length;
                counterElement.textContent = `${currentLength}/${maxLength} characters`;
                
                if (currentLength > maxLength * 0.9) {
                    counterElement.style.color = 'var(--warning-color)';
                } else {
                    counterElement.style.color = 'var(--text-secondary)';
                }
            });
        });
    }
    
    // Initialize any tooltip elements
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    
    if (tooltipTriggers.length > 0) {
        tooltipTriggers.forEach(trigger => {
            const title = trigger.getAttribute('title') || trigger.getAttribute('data-bs-title');
            
            // Simple tooltip implementation
            trigger.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = title;
                
                tooltip.style.position = 'absolute';
                tooltip.style.backgroundColor = 'var(--background-secondary)';
                tooltip.style.color = 'var(--text-primary)';
                tooltip.style.padding = '0.5rem 1rem';
                tooltip.style.borderRadius = 'var(--border-radius)';
                tooltip.style.boxShadow = 'var(--box-shadow)';
                tooltip.style.fontSize = '0.875rem';
                tooltip.style.zIndex = '1000';
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.top = `${rect.bottom + window.scrollY + 10}px`;
                tooltip.style.left = `${rect.left + window.scrollX + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
                
                this.addEventListener('mouseleave', function onMouseLeave() {
                    document.body.removeChild(tooltip);
                    this.removeEventListener('mouseleave', onMouseLeave);
                });
            });
        });
    }
    
    // Add animation classes to elements when they scroll into view
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        const isElementInViewport = (el) => {
            const rect = el.getBoundingClientRect();
            return (
                rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8
            );
        };
        
        const animateElements = () => {
            animatedElements.forEach(element => {
                if (isElementInViewport(element) && !element.classList.contains('animated')) {
                    element.classList.add('animated');
                    
                    const animation = element.getAttribute('data-animation') || 'fade-in';
                    element.classList.add(animation);
                }
            });
        };
        
        // Initial check
        animateElements();
        
        // Check on scroll
        window.addEventListener('scroll', animateElements);
    }
});
