const toasts = document.querySelectorAll('.toast');

function hideToast () {
    setTimeout(() => {
        toasts.forEach(el => {
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 500);
        });
    }, 3000);
}

hideToast();