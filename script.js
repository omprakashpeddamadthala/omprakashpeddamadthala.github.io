document.addEventListener('DOMContentLoaded', function() {

    // Smooth Scrolling for Navbar Links
    const navLinks = document.querySelectorAll('header nav ul li a[href^="#"]');
    const headerElement = document.querySelector('header');
    let headerHeight = headerElement ? headerElement.offsetHeight : 80; // Default or dynamic header height

    // Recalculate header height on resize, especially for responsive headers
    window.addEventListener('resize', () => {
        headerHeight = headerElement ? headerElement.offsetHeight : 80;
    });

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            let targetId = this.getAttribute('href');
            let targetElement = document.querySelector(targetId);

            if (targetElement) {
                let targetPosition = targetElement.offsetTop;
                let offsetPosition = targetPosition - headerHeight;

                // Check if header is fixed or static based on window width (matches CSS @media query for header becoming static)
                if (window.innerWidth <= 768) { // When header is static
                    offsetPosition = targetPosition; // No offset needed, or a smaller one if there's still some fixed element
                }

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Optional: Close mobile menu if open
                // if (nav.classList.contains('active')) { // Assuming a class 'active' for mobile menu visibility
                //     nav.classList.remove('active');
                // }
            }
        });
    });

    // Update Copyright Year
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Active Link Highlighting on Scroll
    const sections = document.querySelectorAll('main section[id]');
    const navbarLinks = document.querySelectorAll('header nav ul li a');

    function changeLinkState() {
        let currentSectionId = '';
        // Use a slightly adjusted scroll position for fixed header scenarios
        // The offset should be a bit more than the header height to ensure the section is well in view
        const scrollPosition = window.pageYOffset + headerHeight + 50;


        sections.forEach(section => {
            if (scrollPosition >= section.offsetTop) {
                currentSectionId = section.id;
            }
        });

        // If no section is "active" (e.g., scrolled to the very top, above the first section),
        // default to making the "hero" or first link active.
        if (!currentSectionId && sections.length > 0) {
             // Check if the scroll is very near the top, above the first actual section
            if (window.pageYOffset < sections[0].offsetTop - headerHeight) {
                 currentSectionId = "hero"; // Default to hero or the first nav item's target
            }
        }


        navbarLinks.forEach(link => {
            link.classList.remove('active');
            // Check href attribute directly for matching section ID
            if (link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });

        // Handle case where no section is matched (e.g. at the very top or bottom of the page beyond sections)
        // If at the very top, make the first link active (usually #hero or similar)
        if (!currentSectionId && navbarLinks.length > 0 && window.pageYOffset < (sections[0] ? sections[0].offsetTop : 200) ) {
            const firstLink = document.querySelector('header nav ul li a[href="#hero"]');
            if (firstLink) {
                firstLink.classList.add('active');
            }
        }
    }

    if (sections.length > 0) {
        window.addEventListener('scroll', changeLinkState);
        changeLinkState(); // Initial call
    }

});
