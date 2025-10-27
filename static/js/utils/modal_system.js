/**
 * Modal System - Centralized Modal Management
 * 
 * Provides a consistent modal dialog system across the application.
 * Supports alert, confirm, success, error, and warning modals.
 * 
 * Usage:
 *   await ModalSystem.alert('Message');
 *   const confirmed = await ModalSystem.confirm('Are you sure?');
 *   await ModalSystem.success('Operation successful!');
 *   await ModalSystem.error('An error occurred');
 *   await ModalSystem.warning('Please be careful');
 */

window.ModalSystem = {
    /**
     * Open a modal by ID
     * @param {string} modalId - The ID of the modal element
     */
    openModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('modal-open');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    },
    
    /**
     * Close a modal by ID
     * @param {string} modalId - The ID of the modal element
     */
    closeModal: function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('modal-open');
            setTimeout(() => {
                modal.classList.add('hidden');
                document.body.style.overflow = ''; // Restore scrolling
            }, 200); // Wait for fade out animation
        }
    },
    
    /**
     * Show a custom alert modal
     * @param {string} message - The message to display
     * @param {Object} options - Configuration options
     * @returns {Promise} - Resolves when modal is closed
     */
    alert: function(message, options = {}) {
        const modalId = 'alertModal';
        const icon = options.icon || 'bi-info-circle-fill';
        const iconColor = options.iconColor || 'text-blue-600';
        const iconBg = options.iconBg || 'bg-blue-100';
        const title = options.title || 'Alert';
        const buttonText = options.buttonText || 'OK';
        const buttonClass = options.buttonClass || 'bg-blue-600 hover:bg-blue-700';
        
        // Remove existing alert modal if any
        const existing = document.getElementById(modalId);
        if (existing) existing.remove();
        
        // Create modal HTML
        const modalHtml = `
            <div id="${modalId}" class="modal-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div class="modal-container bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-fade-in">
                    <div class="text-center">
                        <div class="w-16 h-16 ${iconBg} rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="bi ${icon} text-4xl ${iconColor}"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-gray-800 mb-3">${title}</h3>
                        <p class="text-gray-600 mb-6">${message}</p>
                        <button 
                            onclick="ModalSystem.closeModal('${modalId}')"
                            class="px-8 py-3 ${buttonClass} text-white rounded-lg transition font-semibold"
                        >
                            ${buttonText}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.openModal(modalId);
        
        return new Promise(resolve => {
            document.getElementById(modalId).addEventListener('click', function handler(e) {
                if (e.target.tagName === 'BUTTON' || e.target === this) {
                    ModalSystem.closeModal(modalId);
                    setTimeout(() => document.getElementById(modalId).remove(), 300);
                    this.removeEventListener('click', handler);
                    resolve();
                }
            });
        });
    },
    
    /**
     * Show a custom confirm modal
     * @param {string} message - The message to display
     * @param {Object} options - Configuration options
     * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
     */
    confirm: function(message, options = {}) {
        const modalId = 'confirmModal';
        const icon = options.icon || 'bi-question-circle-fill';
        const iconColor = options.iconColor || 'text-yellow-600';
        const iconBg = options.iconBg || 'bg-yellow-100';
        const title = options.title || 'Confirm Action';
        const confirmText = options.confirmText || 'Confirm';
        const cancelText = options.cancelText || 'Cancel';
        const confirmClass = options.confirmClass || 'bg-blue-600 hover:bg-blue-700';
        const cancelClass = options.cancelClass || 'bg-gray-300 hover:bg-gray-400 text-gray-700';
        
        // Remove existing confirm modal if any
        const existing = document.getElementById(modalId);
        if (existing) existing.remove();
        
        // Create modal HTML
        const modalHtml = `
            <div id="${modalId}" class="modal-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div class="modal-container bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-fade-in">
                    <div class="text-center">
                        <div class="w-16 h-16 ${iconBg} rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="bi ${icon} text-4xl ${iconColor}"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-gray-800 mb-3">${title}</h3>
                        <p class="text-gray-600 mb-6">${message}</p>
                        <div class="flex gap-3 justify-center">
                            <button 
                                id="${modalId}-confirm"
                                class="px-6 py-3 ${confirmClass} text-white rounded-lg transition font-semibold"
                            >
                                ${confirmText}
                            </button>
                            <button 
                                id="${modalId}-cancel"
                                class="px-6 py-3 ${cancelClass} rounded-lg transition font-semibold"
                            >
                                ${cancelText}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.openModal(modalId);
        
        return new Promise(resolve => {
            document.getElementById(`${modalId}-confirm`).addEventListener('click', function() {
                ModalSystem.closeModal(modalId);
                setTimeout(() => document.getElementById(modalId).remove(), 300);
                resolve(true);
            });
            
            document.getElementById(`${modalId}-cancel`).addEventListener('click', function() {
                ModalSystem.closeModal(modalId);
                setTimeout(() => document.getElementById(modalId).remove(), 300);
                resolve(false);
            });
            
            // Cancel on outside click
            document.getElementById(modalId).addEventListener('click', function(e) {
                if (e.target === this) {
                    ModalSystem.closeModal(modalId);
                    setTimeout(() => document.getElementById(modalId).remove(), 300);
                    resolve(false);
                }
            });
        });
    },
    
    /**
     * Show a success modal
     * @param {string} message - The success message
     * @param {Object} options - Additional configuration options
     * @returns {Promise} - Resolves when modal is closed
     */
    success: function(message, options = {}) {
        return this.alert(message, {
            ...options,
            icon: 'bi-check-circle-fill',
            iconColor: 'text-green-600',
            iconBg: 'bg-green-100',
            title: options.title || 'Success',
            buttonClass: 'bg-green-600 hover:bg-green-700'
        });
    },
    
    /**
     * Show an error modal
     * @param {string} message - The error message
     * @param {Object} options - Additional configuration options
     * @returns {Promise} - Resolves when modal is closed
     */
    error: function(message, options = {}) {
        return this.alert(message, {
            ...options,
            icon: 'bi-x-circle-fill',
            iconColor: 'text-red-600',
            iconBg: 'bg-red-100',
            title: options.title || 'Error',
            buttonClass: 'bg-red-600 hover:bg-red-700'
        });
    },
    
    /**
     * Show a warning modal
     * @param {string} message - The warning message
     * @param {Object} options - Additional configuration options
     * @returns {Promise} - Resolves when modal is closed
     */
    warning: function(message, options = {}) {
        return this.alert(message, {
            ...options,
            icon: 'bi-exclamation-triangle-fill',
            iconColor: 'text-yellow-600',
            iconBg: 'bg-yellow-100',
            title: options.title || 'Warning',
            buttonClass: 'bg-yellow-600 hover:bg-yellow-700'
        });
    }
};

// Global shortcuts for backward compatibility
window.openModal = ModalSystem.openModal.bind(ModalSystem);
window.closeModal = ModalSystem.closeModal.bind(ModalSystem);

// ESC key to close topmost modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal-overlay.modal-open');
        if (openModals.length > 0) {
            const topModal = openModals[openModals.length - 1];
            ModalSystem.closeModal(topModal.id);
        }
    }
});
