// Main JavaScript file
document.addEventListener('DOMContentLoaded', () => {
  // Mobile menu toggle
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // Close mobile menu on outside click
  document.addEventListener('click', (e) => {
    if (mobileMenu && !mobileMenu.contains(e.target) &&
        mobileMenuButton && !mobileMenuButton.contains(e.target)) {
      mobileMenu.classList.add('hidden');
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href').slice(1);
      const target = document.getElementById(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Copy link to clipboard
  const copyLinkButtons = document.querySelectorAll('[data-copy-link]');
  copyLinkButtons.forEach(button => {
    button.addEventListener('click', async () => {
      const url = window.location.href;
      try {
        await navigator.clipboard.writeText(url);
        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = 'Copy Link';
        }, 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    });
  });

  // Toggle password visibility in forms
  const passwordToggles = document.querySelectorAll('[data-toggle-password]');
  passwordToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const input = document.querySelector(toggle.dataset.target);
      if (input) {
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
        toggle.classList.toggle('text-primary-600');
      }
    });
  });

  // Auto-hide alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.classList.add('opacity-0', 'transition-opacity', 'duration-300');
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });
});
