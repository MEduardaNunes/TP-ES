const toasts = document.querySelectorAll('.toast');

function hideToast () {
    setTimeout(() => {
        toasts.forEach(el => {
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 200);
        });
    }, 1200);
}

hideToast();

// Simple immediate-submit buttons for profile icons
document.querySelectorAll('[data-icon-clear-submit="1"]').forEach((button) => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const form = button.closest('form');
        if (form) {
            const hiddenInput = document.getElementById(button.getAttribute('data-icon-clear-target'));
            if (hiddenInput) {
                hiddenInput.value = '1';
            }
            const emojiTarget = button.getAttribute('data-icon-clear-emoji-target');
            if (emojiTarget) {
                const emojiInput = document.getElementById(emojiTarget);
                if (emojiInput) emojiInput.value = '1';
            }
            const fileId = button.getAttribute('data-icon-clear-file');
            if (fileId) {
                const fileInput = document.getElementById(fileId);
                if (fileInput) fileInput.value = '';
            }
            form.submit();
        }
    });
});

function bindIconClearButtons() {
    document.querySelectorAll('[data-icon-clear-target]:not([data-icon-clear-submit])').forEach((button) => {
        const hiddenInput = document.getElementById(button.getAttribute('data-icon-clear-target'));
        const emojiHiddenInputId = button.getAttribute('data-icon-clear-emoji-target');
        const emojiHiddenInput = emojiHiddenInputId ? document.getElementById(emojiHiddenInputId) : null;
        const fileInputId = button.getAttribute('data-icon-clear-file');
        const fileInput = fileInputId ? document.getElementById(fileInputId) : null;
        const submitImmediately = button.getAttribute('data-icon-clear-submit') === '1';

        if (!hiddenInput) {
            return;
        }

        const syncState = () => {
            const isCleared = hiddenInput.value === '1';
            button.classList.toggle('icon-clear-btn--active', isCleared);
            button.setAttribute('aria-pressed', isCleared ? 'true' : 'false');
        };

        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            hiddenInput.value = '1';
            if (emojiHiddenInput) {
                emojiHiddenInput.value = '1';
            }
            if (fileInput) {
                fileInput.value = '';
            }

            if (submitImmediately) {
                const form = button.closest('form');
                if (form) {
                    setTimeout(() => form.submit(), 0);
                }
            } else {
                syncState();
            }
        });

        if (fileInput) {
            fileInput.addEventListener('change', () => {
                hiddenInput.value = '';
                if (emojiHiddenInput) {
                    emojiHiddenInput.value = '';
                }
                syncState();
            });
        }

        // Only initialize visual state for modal buttons, not for immediate-submit buttons
        if (!submitImmediately) {
            syncState();
        }
    });
}

function hideToasts() {
    const toasts = document.querySelectorAll('.toast');
    if (toasts.length > 0) {
        setTimeout(() => {
            toasts.forEach(el => {
                el.style.opacity = "0";
                setTimeout(() => el.remove(), 400);
            });
        }, 2000);
    }
}

function bindIconClearButtons() {
    document.querySelectorAll('[data-icon-clear-target]').forEach((button) => {
        const targetId = button.getAttribute('data-icon-clear-target');
        const hiddenInput = document.getElementById(targetId);
        if (!hiddenInput) return;

        button.addEventListener('click', (e) => {
            e.preventDefault();
            hiddenInput.value = '1';
            
            // Se for envio imediato (ex: perfil)
            if (button.getAttribute('data-icon-clear-submit') === '1') {
                button.closest('form')?.submit();
            } else {
                button.classList.add('icon-clear-btn--active');
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    hideToasts();
    bindIconClearButtons();
});
