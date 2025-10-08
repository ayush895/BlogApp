// Toast auto-show and hide
window.onload = function () {
    let toasts = document.querySelectorAll(".toast");
    toasts.forEach((toast, index) => {
        // Show with small delay
        setTimeout(() => toast.classList.add("show"), 200 * index);
        // Hide after 4 seconds
        setTimeout(() => toast.classList.remove("show"), 4000 + 200 * index);
    });
};