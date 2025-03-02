document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.querySelector('.gallery');
    const prevButton = document.getElementById('prev');
    const nextButton = document.getElementById('next');
    const dots = document.querySelectorAll('.dot');
    const items = document.querySelectorAll('.gallery-item');
    
    let currentIndex = 0;
    const totalItems = items.length;
    
    // Initialize gallery
    function showItem(index) {
        // Hide all items
        items.forEach(item => {
            item.classList.add('hidden');
            item.classList.remove('active');
        });
        
        // Show the selected item
        items[index].classList.remove('hidden');
        items[index].classList.add('active');
        
        // Update dots
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        
        // Update buttons
        prevButton.disabled = index === 0;
        nextButton.disabled = index === totalItems - 1;
        
        currentIndex = index;
    }
    
    // Navigation handlers
    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            showItem(currentIndex - 1);
        }
    });
    
    nextButton.addEventListener('click', () => {
        if (currentIndex < totalItems - 1) {
            showItem(currentIndex + 1);
        }
    });
    
    // Dots navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showItem(index);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            if (currentIndex > 0) {
                showItem(currentIndex - 1);
            }
        } else if (e.key === 'ArrowRight') {
            if (currentIndex < totalItems - 1) {
                showItem(currentIndex + 1);
            }
        }
    });
    
    // Initialize with first item
    showItem(0);
});