document.addEventListener('DOMContentLoaded', function() {

    // Smooth Scrolling for Navbar Links
    const navLinks = document.querySelectorAll('#navbar ul li a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            let targetId = this.getAttribute('href');
            // Adjust for fixed header height if header is always visible and fixed
            // For this example, assuming direct scroll to element is fine or CSS handles offset
            let targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Calculate position, considering fixed header if it's consistently fixed height
                const headerOffset = document.getElementById('header').offsetHeight || 70; // Fallback if not found
                const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Update Copyright Year
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Active Link Highlighting on Scroll (Basic Implementation)
    const sections = document.querySelectorAll('section[id]'); // All sections with an ID
    const navbarLinks = document.querySelectorAll('#navbar ul li a');

    function changeLinkState() {
        let index = sections.length;
        const headerHeight = document.getElementById('header').offsetHeight || 70;

        while(--index && window.scrollY + headerHeight * 1.5 < sections[index].offsetTop) {} // Adjusted offset for better trigger

        navbarLinks.forEach((link) => link.classList.remove('active'));
        // Check if a corresponding link exists before trying to add 'active' class
        if (sections[index]) {
            const activeLink = document.querySelector(`#navbar ul li a[href*="${sections[index].id}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        } else if (window.scrollY < sections[0].offsetTop - headerHeight * 1.5) {
            // If above the first section (e.g. very top of hero), make home active
            const homeLink = document.querySelector(`#navbar ul li a[href*="#hero"]`);
            if (homeLink) {
                homeLink.classList.add('active');
            }
        }
    }

    // Initial call to set active link on page load (e.g. if page is loaded scrolled or with a hash)
    if (sections.length > 0) { // Ensure sections are present
       changeLinkState();
    }
    window.addEventListener('scroll', changeLinkState);

    // Optional: Change header style on scroll
    const header = document.getElementById('header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) { // Add shadow or change background after scrolling 50px
                header.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                // header.style.backgroundColor = 'rgba(255, 255, 255, 0.95)'; // Example: slightly transparent
            } else {
                header.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                // header.style.backgroundColor = '#fff';
            }
        });
    }

});
