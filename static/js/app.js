// AI Code Analyzer - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeThemeToggle();
    initializeFileUpload();
    initializeSyntaxHighlighting();
    initializeTooltips();
});

// Theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;

    if (!themeToggle || !themeIcon) return;

    // Get saved theme or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-bs-theme', currentTheme);
    updateThemeIcon(currentTheme);

    themeToggle.addEventListener('click', function() {
        const newTheme = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        updatePrismTheme(newTheme);
    });

    function updateThemeIcon(theme) {
        if (themeIcon) {
            themeIcon.setAttribute('data-feather', theme === 'light' ? 'moon' : 'sun');
            feather.replace();
        }
    }

    function updatePrismTheme(theme) {
        const prismLight = document.querySelector('link[href*="prism.min.css"]');
        const prismDark = document.getElementById('prism-dark-theme');
        
        if (theme === 'dark') {
            if (prismLight) prismLight.disabled = true;
            if (prismDark) prismDark.disabled = false;
        } else {
            if (prismLight) prismLight.disabled = false;
            if (prismDark) prismDark.disabled = true;
        }
    }

    // Initialize Prism theme on load
    updatePrismTheme(currentTheme);
}

// File upload functionality
function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const selectedFileName = document.getElementById('selectedFileName');
    const submitBtn = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');

    if (!uploadArea || !fileInput) return;

    // Click to upload
    uploadArea.addEventListener('click', function(e) {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Form submission with loading state
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            showUploadProgress();
        });
    }

    function handleFileSelection(file) {
        const maxSize = 16 * 1024 * 1024; // 16MB
        const allowedTypes = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', 
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.sh', 
            '.sql', '.html', '.css', '.json', '.xml', '.yaml', '.yml', 
            '.txt', '.md'
        ];

        // Check file size
        if (file.size > maxSize) {
            showAlert('File too large. Maximum size is 16MB.', 'error');
            return;
        }

        // Check file type
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            showAlert('Unsupported file type. Please upload a code file.', 'error');
            return;
        }

        // Update UI
        if (selectedFileName) {
            selectedFileName.textContent = file.name;
        }
        
        if (fileInfo) {
            fileInfo.classList.remove('d-none');
        }
        
        if (submitBtn) {
            submitBtn.disabled = false;
        }

        // Set the file input
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
    }

    function showUploadProgress() {
        const uploadContent = uploadArea.querySelector('.upload-content');
        const uploadProgress = document.getElementById('uploadProgress');
        const fileName = document.getElementById('fileName');
        
        if (uploadContent && uploadProgress && fileName) {
            uploadContent.classList.add('d-none');
            uploadProgress.classList.remove('d-none');
            fileName.textContent = fileInput.files[0].name;
        }
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
        }
    }
}

// Syntax highlighting initialization
function initializeSyntaxHighlighting() {
    // Configure Prism.js
    if (typeof Prism !== 'undefined') {
        Prism.manual = false;
        
        // Add line numbers to code blocks
        document.querySelectorAll('pre code').forEach(function(block) {
            if (!block.classList.contains('line-numbers')) {
                block.classList.add('line-numbers');
            }
        });
        
        // Re-highlight all code blocks
        Prism.highlightAll();
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.classList.remove('show');
                setTimeout(() => {
                    if (alertContainer.parentNode) {
                        alertContainer.remove();
                    }
                }, 150);
            }
        }, 5000);
    }
}

// Copy to clipboard functionality
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.innerHTML;
        button.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
        button.classList.remove('btn-outline-secondary');
        button.classList.add('btn-success');
        
        feather.replace();
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
            feather.replace();
        }, 2000);
    }).catch(function(err) {
        showAlert('Failed to copy to clipboard', 'error');
    });
}

// Export functionality
function exportAnalysis(analysisId) {
    fetch(`/export/${analysisId}`)
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analysis_${data.filename}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(error => {
            showAlert('Failed to export analysis', 'error');
        });
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Auto-refresh feather icons when content changes
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Check if any added nodes contain feather icons
            const hasFeatherIcons = Array.from(mutation.addedNodes).some(node => {
                return node.nodeType === Node.ELEMENT_NODE && 
                       (node.querySelector && node.querySelector('[data-feather]') || 
                        node.hasAttribute && node.hasAttribute('data-feather'));
            });
            
            if (hasFeatherIcons) {
                feather.replace();
            }
        }
    });
});

// Start observing
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search (if implemented)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + U to go to upload page
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        window.location.href = '/upload';
    }
    
    // Ctrl/Cmd + D to go to dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        window.location.href = '/dashboard';
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            if (perfData && perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                console.warn('Page load time is high:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }
        }, 0);
    });
}
