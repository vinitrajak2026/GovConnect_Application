document.addEventListener('DOMContentLoaded', () => {
  // --- 1. DARK / LIGHT THEME TOGGLE ---
  const themeToggle = document.getElementById('themeToggleBtn');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('govconnect-theme', newTheme);
      
      // Update toggle icon
      themeToggle.innerHTML = newTheme === 'light' ? '🌙' : '☀️';
    });

    // Load saved theme preference
    const savedTheme = localStorage.getItem('govconnect-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.innerHTML = savedTheme === 'light' ? '🌙' : '☀️';
  }

  // --- 2. ACCESSIBILITY CONTROLS (CONTRAST & TEXT SIZE) ---
  const contrastToggle = document.getElementById('contrastToggleBtn');
  if (contrastToggle) {
    contrastToggle.addEventListener('click', () => {
      const contrastState = document.documentElement.getAttribute('data-contrast') || 'normal';
      const nextContrast = contrastState === 'normal' ? 'high' : 'normal';
      document.documentElement.setAttribute('data-contrast', nextContrast);
      localStorage.setItem('govconnect-contrast', nextContrast);
    });
    
    // Load saved contrast preference
    const savedContrast = localStorage.getItem('govconnect-contrast') || 'normal';
    document.documentElement.setAttribute('data-contrast', savedContrast);
  }

  // Font resizers
  const textIncrease = document.getElementById('textIncreaseBtn');
  const textDecrease = document.getElementById('textDecreaseBtn');
  const textReset = document.getElementById('textResetBtn');

  if (textIncrease && textDecrease && textReset) {
    let currentScale = parseFloat(localStorage.getItem('govconnect-text-scale') || '1.0');
    
    const applyScale = (scale) => {
      document.documentElement.style.fontSize = `${scale * 100}%`;
      localStorage.setItem('govconnect-text-scale', scale);
    };

    textIncrease.addEventListener('click', () => {
      if (currentScale < 1.3) {
        currentScale += 0.1;
        applyScale(currentScale);
      }
    });

    textDecrease.addEventListener('click', () => {
      if (currentScale > 0.8) {
        currentScale -= 0.1;
        applyScale(currentScale);
      }
    });

    textReset.addEventListener('click', () => {
      currentScale = 1.0;
      applyScale(currentScale);
    });

    // Apply saved scale
    applyScale(currentScale);
  }

  // --- 3. AUTOCOMPLETE GLOBAL SEARCH SUGGESTIONS ---
  const searchInput = document.getElementById('globalSearchInput');
  const suggestionsBox = document.getElementById('globalSuggestionsBox');

  if (searchInput && suggestionsBox) {
    let delayTimer;

    searchInput.addEventListener('input', () => {
      clearTimeout(delayTimer);
      const query = searchInput.value.trim();

      if (query.length < 2) {
        suggestionsBox.style.display = 'none';
        return;
      }

      delayTimer = setTimeout(() => {
        fetch(`/search/?suggest=true&q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            suggestionsBox.innerHTML = '';
            const list = data.suggestions || [];
            
            if (list.length === 0) {
              suggestionsBox.style.display = 'none';
              return;
            }

            list.forEach(item => {
              const anchor = document.createElement('a');
              anchor.className = 'suggestion-item';
              anchor.href = item.url;
              anchor.innerHTML = `
                <span>${item.title}</span>
                <span class="badge badge-category">${item.type}</span>
              `;
              suggestionsBox.appendChild(anchor);
            });

            suggestionsBox.style.display = 'block';
          })
          .catch(err => console.error('Error fetching suggestions:', err));
      }, 300);
    });

    // Hide search suggestions on document click
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.style.display = 'none';
      }
    });
  }

  // --- 4. AJAX BOOKMARK MANAGER TOGGLING ---
  const bookmarkButtons = document.querySelectorAll('.bookmark-toggle-btn');
  bookmarkButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      
      const model = btn.getAttribute('data-model');
      const id = btn.getAttribute('data-id');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      const formData = new FormData();
      formData.append('model', model);
      formData.append('id', id);

      fetch('/bookmark/toggle/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (data.action === 'added') {
            btn.classList.add('btn-gov-secondary');
            btn.classList.remove('btn-outline-secondary');
            btn.innerHTML = '❤️ Saved';
          } else {
            btn.classList.remove('btn-gov-secondary');
            btn.classList.add('btn-outline-secondary');
            btn.innerHTML = '🤍 Save';
          }
        } else {
          alert('Failed to save bookmark. Please make sure you are logged in.');
        }
      })
      .catch(err => {
        console.error('Bookmark toggle error:', err);
        alert('Authentication needed to bookmark resources.');
      });
    });
  });
});
