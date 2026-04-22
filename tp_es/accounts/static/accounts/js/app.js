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
