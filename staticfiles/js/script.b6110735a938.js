document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Set current year in footer
    const currentYearElements = document.querySelectorAll('#currentYear');
    currentYearElements.forEach(element => {
        element.textContent = new Date().getFullYear();
    });
    
    // Example tabs functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const exampleCards = document.querySelectorAll('.example-card');
    
    if (tabButtons.length && exampleCards.length) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                tabButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const category = this.dataset.tab;
                
                // Show/hide example cards based on category
                exampleCards.forEach(card => {
                    if (category === 'all' || card.dataset.category === category) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Animate elements on scroll
    const animateElements = document.querySelectorAll('.feature-card, .step-card, .example-card, .pricing-card, .testimonial-card');
    
    // Set initial state
    animateElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // Function to check if element is in viewport
    function isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.9
        );
    }
    
    // Function to handle scroll animation
    function handleScrollAnimation() {
        animateElements.forEach(element => {
            if (isInViewport(element)) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScrollAnimation);
    
    // Trigger on initial load
    setTimeout(handleScrollAnimation, 100);
    
    // Suggestion chips functionality
    const suggestionChips = document.querySelectorAll('.chip');
    const demoTextarea = document.querySelector('.demo-input textarea');
    
    if (suggestionChips.length && demoTextarea) {
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', function() {
                const chipType = this.textContent.trim();
                let suggestion = '';
                
                switch(chipType) {
                    case 'Portfolio':
                        suggestion = 'I need a portfolio website for a photographer with a dark theme, gallery section, about page, and contact form.';
                        break;
                    case 'E-commerce':
                        suggestion = 'Create an e-commerce website for a clothing brand with product listings, shopping cart, checkout, and customer account pages.';
                        break;
                    case 'Blog':
                        suggestion = 'Design a blog website with a clean layout, featured posts section, categories, search functionality, and newsletter signup.';
                        break;
                    case 'Business':
                        suggestion = 'Build a business website for a marketing agency with services section, case studies, team profiles, testimonials, and contact information.';
                        break;
                    default:
                        suggestion = '';
                }
                
                demoTextarea.value = suggestion;
            });
        });
    }
    
    // Generate website button functionality
    const generateButton = document.querySelector('.demo-input .btn-primary');
    const previewPlaceholder = document.querySelector('.preview-placeholder');
    
    if (generateButton && previewPlaceholder) {
        generateButton.addEventListener('click', function() {
            const userInput = demoTextarea.value.trim();
            
            if (userInput) {
                // Show loading state
                previewPlaceholder.innerHTML = `
                    <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="2" fill="none" class="loading-spinner">
                        <circle cx="12" cy="12" r="10" stroke-dasharray="30 60"></circle>
                    </svg>
                    <p>Generating your website...</p>
                `;
                
                // Add loading spinner animation
                const spinner = document.querySelector('.loading-spinner');
                if (spinner) {
                    spinner.style.animation = 'spin 1s linear infinite';
                }
                
                // Simulate generation process (would be replaced with actual API call)
                setTimeout(() => {
                    // Show success state
                    previewPlaceholder.innerHTML = `
                        <svg viewBox="0 0 24 24" width="48" height="48" stroke="#6366f1" stroke-width="2" fill="none">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        <p style="color: #6366f1">Website successfully generated!</p>
                        <a href="#" class="btn btn-primary btn-small" style="margin-top: 1rem;">View Preview</a>
                    `;
                }, 3000);
            }
        });
    }
    
    // Testimonial slider functionality
    const navDots = document.querySelectorAll('.nav-dot');
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    
    if (navDots.length && testimonialCards.length) {
        navDots.forEach((dot, index) => {
            dot.addEventListener('click', function() {
                // Remove active class from all dots
                navDots.forEach(d => d.classList.remove('active'));
                
                // Add active class to clicked dot
                this.classList.add('active');
                
                // Hide all testimonial cards
                testimonialCards.forEach(card => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(20px)';
                });
                
                // Show selected testimonial card
                setTimeout(() => {
                    testimonialCards.forEach(card => {
                        card.style.display = 'none';
                    });
                    
                    if (testimonialCards[index]) {
                        testimonialCards[index].style.display = 'block';
                        setTimeout(() => {
                            testimonialCards[index].style.opacity = '1';
                            testimonialCards[index].style.transform = 'translateX(0)';
                        }, 50);
                    }
                }, 300);
            });
        });
    }
});

// Add keyframes for spinner animation
const style = document.createElement('style');
style.textContent = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);