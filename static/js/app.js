document.addEventListener('DOMContentLoaded', function() {
    console.log('AMS Core application loaded');
    
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(toastElement => {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    });
});

function showMessage(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const mainContainer = document.querySelector('main .container-fluid');
    if (mainContainer) {
        mainContainer.insertBefore(alertElement, mainContainer.firstChild);
    }
}
