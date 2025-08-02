// Main JavaScript for CPE Management Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            const preview = document.getElementById(input.id + '_preview');
            
            if (preview && file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (file.type.startsWith('image/')) {
                        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">`;
                    } else {
                        preview.innerHTML = `<p class="text-muted"><i class="fas fa-file-alt me-2"></i>${file.name}</p>`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Dynamic progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = width;
        }, 200);
    });

    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = button.getAttribute('data-confirm-delete') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-save form data to localStorage
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    autoSaveForms.forEach(function(form) {
        const formId = form.id || 'auto-save-form';
        
        // Load saved data
        const savedData = localStorage.getItem(formId);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(function(key) {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && input.type !== 'password') {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.warn('Failed to load saved form data:', e);
            }
        }
        
        // Save data on change
        form.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (key !== 'csrf_token' && !key.includes('password')) {
                    data[key] = value;
                }
            }
            localStorage.setItem(formId, JSON.stringify(data));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            setTimeout(function() {
                localStorage.removeItem(formId);
            }, 1000);
        });
    });

    // CPE value calculator
    const cpeInputs = document.querySelectorAll('input[name="cpe_value"]');
    cpeInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseFloat(input.value) || 0;
            const activityType = document.querySelector('select[name="activity_type"]');
            
            if (activityType) {
                const type = activityType.value;
                let suggestion = '';
                
                switch (type) {
                    case 'Training':
                        suggestion = 'Typically 1 CPE per hour of training';
                        break;
                    case 'Conference':
                        suggestion = 'Usually 1-8 CPEs per day';
                        break;
                    case 'Webinar':
                        suggestion = 'Generally 1-2 CPEs per session';
                        break;
                    case 'Self-Study':
                        suggestion = 'Varies by authority (1 CPE per 1-4 hours)';
                        break;
                }
                
                const helpText = input.parentNode.parentNode.querySelector('.form-text');
                if (helpText && suggestion) {
                    helpText.textContent = suggestion;
                }
            }
        });
    });

    // Search functionality for tables
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = input.value.toLowerCase();
            const tableId = input.getAttribute('data-table-search');
            const table = document.getElementById(tableId);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });

    // Deadline reminders
    function checkDeadlines() {
        const today = new Date();
        const deadlineElements = document.querySelectorAll('[data-renewal-date]');
        
        deadlineElements.forEach(function(element) {
            const renewalDate = new Date(element.getAttribute('data-renewal-date'));
            const daysUntil = Math.ceil((renewalDate - today) / (1000 * 60 * 60 * 24));
            
            if (daysUntil <= 90 && daysUntil > 0) {
                element.classList.add('deadline-warning');
                
                if (daysUntil <= 30) {
                    element.classList.add('deadline-urgent');
                }
            }
        });
    }
    
    checkDeadlines();

    // Export functionality with loading states
    const exportButtons = document.querySelectorAll('[data-export]');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            button.classList.add('btn-loading');
            button.disabled = true;
            
            setTimeout(function() {
                button.classList.remove('btn-loading');
                button.disabled = false;
            }, 3000);
        });
    });

    // Dashboard chart initialization (if Chart.js is available)
    if (typeof Chart !== 'undefined') {
        const chartElements = document.querySelectorAll('[data-chart]');
        chartElements.forEach(function(element) {
            const chartType = element.getAttribute('data-chart');
            const ctx = element.getContext('2d');
            
            // Example progress chart
            if (chartType === 'progress') {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Completed', 'Remaining'],
                        datasets: [{
                            data: [
                                parseFloat(element.getAttribute('data-completed') || 0),
                                parseFloat(element.getAttribute('data-remaining') || 0)
                            ],
                            backgroundColor: ['#198754', '#e9ecef'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        });
    }
});

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container').firstElementChild;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(function() {
        alertDiv.remove();
    }, 5000);
}

function validateFileType(file, allowedTypes) {
    const fileType = file.type.toLowerCase();
    return allowedTypes.some(type => fileType.includes(type));
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Progressive Web App functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K for search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});
