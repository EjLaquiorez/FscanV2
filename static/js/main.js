// Main JavaScript for Fruit Quality Scanner

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const previewSection = document.getElementById('previewSection');
    const imagePreview = document.getElementById('imagePreview');
    const scanBtn = document.getElementById('scanBtn');
    const clearBtn = document.getElementById('clearBtn');
    const cameraBtn = document.getElementById('cameraBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorMessage = document.getElementById('errorMessage');

    let selectedFile = null;

    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            handleFileSelect(e.target.files[0]);
        });
    }

    // Upload area click handler
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.style.background = '#e8f5e9';
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.style.background = '#f8f9fa';
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.background = '#f8f9fa';
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
    }

    // Handle file selection
    function handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showError('Please select an image file.');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            showError('Image size should be less than 10MB.');
            return;
        }

        selectedFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            previewSection.style.display = 'block';
            uploadArea.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    // Clear button handler
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            selectedFile = null;
            fileInput.value = '';
            previewSection.style.display = 'none';
            uploadArea.style.display = 'flex';
            imagePreview.src = '';
        });
    }

    // Scan button handler
    if (scanBtn) {
        scanBtn.addEventListener('click', function() {
            if (!selectedFile) {
                showError('Please select an image first.');
                return;
            }

            scanImage(selectedFile);
        });
    }

    // Camera button handler
    if (cameraBtn) {
        cameraBtn.addEventListener('click', function() {
            openCamera();
        });
    }

    // Scan image function
    function scanImage(file) {
        showLoading();

        const formData = new FormData();
        formData.append('image', file);

        fetch('/api/detect', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            return response.json().then(data => {
                if (!response.ok) {
                    // Server returned error response
                    throw new Error(data.error || `Scan failed (${response.status}). Please try again.`);
                }
                return data;
            });
        })
        .then(data => {
            hideLoading();
            if (data.success) {
                // Redirect to results page
                window.location.href = `/results/${data.scan_id}`;
            } else {
                // Show detailed error if available
                let errorMsg = data.error || 'Scan failed. Please try again.';
                if (data.traceback && console) {
                    console.error('Server error traceback:', data.traceback);
                }
                showError(errorMsg);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Scan error:', error);
            showError(error.message || 'An error occurred. Please try again.');
        });
    }

    // Camera function
    function openCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showError('Camera is not available in your browser.');
            return;
        }

        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                // Create camera modal
                const cameraModal = document.createElement('div');
                cameraModal.className = 'camera-modal';
                cameraModal.innerHTML = `
                    <div class="camera-container">
                        <video id="cameraVideo" autoplay></video>
                        <div class="camera-controls">
                            <button class="btn btn-primary" id="captureBtn">Capture</button>
                            <button class="btn btn-secondary" id="cancelCameraBtn">Cancel</button>
                        </div>
                    </div>
                `;
                document.body.appendChild(cameraModal);

                const video = document.getElementById('cameraVideo');
                video.srcObject = stream;

                const captureBtn = document.getElementById('captureBtn');
                const cancelBtn = document.getElementById('cancelCameraBtn');

                captureBtn.addEventListener('click', function() {
                    // Capture image
                    const canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    
                    canvas.toBlob(function(blob) {
                        // Stop camera
                        stream.getTracks().forEach(track => track.stop());
                        document.body.removeChild(cameraModal);
                        
                        // Handle captured image
                        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                        handleFileSelect(file);
                    }, 'image/jpeg');
                });

                cancelBtn.addEventListener('click', function() {
                    stream.getTracks().forEach(track => track.stop());
                    document.body.removeChild(cameraModal);
                });
            })
            .catch(function(error) {
                showError('Could not access camera: ' + error.message);
            });
    }

    // Loading overlay functions
    function showLoading() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    function hideLoading() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    // Error message function
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(function() {
                errorMessage.style.display = 'none';
            }, 5000);
        } else {
            alert(message);
        }
    }

    // Export button handler (for results page)
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            exportResults();
        });
    }

    // Freshness Analysis Modal handlers
    const freshnessAnalysisBtn = document.getElementById('freshnessAnalysisBtn');
    const freshnessModal = document.getElementById('freshnessModal');
    const closeModal = document.getElementById('closeModal');
    const closeModalBtn = document.getElementById('closeModalBtn');

    if (freshnessAnalysisBtn && freshnessModal) {
        freshnessAnalysisBtn.addEventListener('click', function() {
            freshnessModal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        });
    }

    function closeFreshnessModal() {
        if (freshnessModal) {
            freshnessModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    }

    if (closeModal) {
        closeModal.addEventListener('click', closeFreshnessModal);
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeFreshnessModal);
    }

    // Close modal when clicking outside
    if (freshnessModal) {
        freshnessModal.addEventListener('click', function(e) {
            if (e.target === freshnessModal) {
                closeFreshnessModal();
            }
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && freshnessModal && freshnessModal.style.display === 'flex') {
            closeFreshnessModal();
        }
    });

    // History filters & interactions
    const historyTableBody = document.querySelector('.history-table tbody');
    if (historyTableBody) {
        const historyRows = Array.from(historyTableBody.querySelectorAll('tr'));
        const searchInput = document.getElementById('historySearch');
        const fruitFilter = document.getElementById('fruitFilter');
        const statusFilter = document.getElementById('statusFilter');
        const dateFilter = document.getElementById('dateFilter');
        const emptyMessage = document.getElementById('historyEmptyMessage');
        const refreshBtn = document.getElementById('historyRefreshBtn');

        function isWithinRange(dateString, range) {
            if (!range || !dateString) return true;
            const rowDate = new Date(dateString);
            if (Number.isNaN(rowDate.getTime())) return true;

            const now = new Date();
            let threshold;

            switch (range) {
                case '24h':
                    threshold = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                    break;
                case '7d':
                    threshold = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    break;
                case '30d':
                    threshold = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                    break;
                default:
                    return true;
            }

            return rowDate >= threshold;
        }

        function applyHistoryFilters() {
            const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
            const fruitValue = fruitFilter ? fruitFilter.value : '';
            const statusValue = statusFilter ? statusFilter.value : '';
            const dateValue = dateFilter ? dateFilter.value : '';

            let visibleCount = 0;

            historyRows.forEach(row => {
                const rowText = row.textContent.toLowerCase();
                const matchesSearch = !searchTerm || rowText.includes(searchTerm);
                const matchesFruit = !fruitValue || row.dataset.fruit === fruitValue;
                const matchesStatus = !statusValue || row.dataset.status === statusValue;
                const matchesDate = isWithinRange(row.dataset.date, dateValue);

                const shouldShow = matchesSearch && matchesFruit && matchesStatus && matchesDate;
                row.style.display = shouldShow ? '' : 'none';
                if (shouldShow) visibleCount += 1;
            });

            if (emptyMessage) {
                emptyMessage.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        }

        if (searchInput) searchInput.addEventListener('input', applyHistoryFilters);
        if (fruitFilter) fruitFilter.addEventListener('change', applyHistoryFilters);
        if (statusFilter) statusFilter.addEventListener('change', applyHistoryFilters);
        if (dateFilter) dateFilter.addEventListener('change', applyHistoryFilters);

        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                window.location.reload();
            });
        }
    }

    // Settings interactions
    const settingsForm = document.getElementById('settingsMasterForm');
    if (settingsForm) {
        const settingsAlert = document.getElementById('settingsAlert');
        const resetBtn = document.getElementById('resetSettingsBtn');
        const toggleInputs = document.querySelectorAll('.toggle-switch input');

        function showSettingsMessage(message, type = 'success') {
            if (!settingsAlert) return;
            settingsAlert.textContent = message;
            settingsAlert.className = `settings-alert ${type}`;
            settingsAlert.style.display = 'block';
            setTimeout(() => {
                settingsAlert.style.display = 'none';
            }, 4000);
        }

        settingsForm.addEventListener('submit', function(event) {
            event.preventDefault();
            showSettingsMessage('Settings saved locally. Update config files to persist.', 'success');
        });

        if (resetBtn) {
            resetBtn.addEventListener('click', function(event) {
                event.preventDefault();
                settingsForm.reset();
                toggleInputs.forEach(toggle => {
                    toggle.checked = toggle.defaultChecked;
                });
                showSettingsMessage('Settings reverted to defaults.', 'success');
            });
        }

        toggleInputs.forEach(toggle => {
            toggle.addEventListener('change', function() {
                const state = toggle.checked ? 'enabled' : 'disabled';
                showSettingsMessage(`${toggle.id.replace('Toggle', '')} ${state}.`, 'success');
            });
        });
    }

    // Export results function
    function exportResults() {
        // Get current URL to extract scan ID
        const pathParts = window.location.pathname.split('/');
        const scanId = pathParts[pathParts.length - 1];

        fetch(`/api/export/${scanId}`, {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Export failed.');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `fruit_scan_${scanId}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            showError('Could not export results.');
            console.error('Error:', error);
        });
    }
});

// Add camera modal styles dynamically
const style = document.createElement('style');
style.textContent = `
    .camera-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        z-index: 2000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .camera-container {
        background: white;
        padding: 20px;
        border-radius: 12px;
        max-width: 90%;
        max-height: 90%;
    }
    #cameraVideo {
        max-width: 100%;
        max-height: 70vh;
        border-radius: 8px;
    }
    .camera-controls {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-top: 20px;
    }
`;
document.head.appendChild(style);

