// Optimized JavaScript for CPE Management Platform

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 4000);
    });

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = width;
        }, 200);
    });

    // Set today's date for activity forms
    const activityDate = document.getElementById('activity_date');
    if (activityDate && !activityDate.value) {
        const today = new Date().toISOString().split('T')[0];
        activityDate.value = today;
    }
});

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.querySelector('.container').prepend(alertDiv);
    setTimeout(() => alertDiv.remove(), 4000);
}