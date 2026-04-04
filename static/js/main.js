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
                // Display results on the right side using data from response
                displayResultsOnPage(data.scan_id, data.results);
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

    // Helper function to get available cameras
    async function getAvailableCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.filter(device => device.kind === 'videoinput');
        } catch (err) {
            console.error('Error enumerating cameras:', err);
            return [];
        }
    }

    // Helper function to switch camera
    async function switchCamera(deviceId, currentStream) {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
        
        const constraints = {
            video: deviceId ? { deviceId: { exact: deviceId } } : true
        };
        
        try {
            const newStream = await navigator.mediaDevices.getUserMedia(constraints);
            const video = document.getElementById('cameraVideo');
            if (video) {
                video.srcObject = newStream;
                video.play().catch(err => {
                    console.error('Error playing video after switch:', err);
                });
            }
            return newStream;
        } catch (error) {
            console.error('Error switching camera:', error);
            showError('Could not switch to selected camera.');
            return null;
        }
    }

    // Helper function to create and setup simple camera modal
    async function setupCameraModal(stream, initialDeviceId = null) {
        // Get available cameras for switching if needed
        const cameras = await getAvailableCameras();
        const currentDeviceId = initialDeviceId || (stream.getVideoTracks()[0]?.getSettings().deviceId);
        
        // Create simple camera modal
        const cameraModal = document.createElement('div');
        cameraModal.className = 'camera-modal';
        cameraModal.innerHTML = `
            <div class="camera-simple-panel">
                <div class="camera-simple-header">
                    <h3 class="camera-simple-title">Camera Preview</h3>
                    <button class="camera-simple-close" id="closeCameraBtn" aria-label="Close">×</button>
                </div>
                
                <div class="camera-simple-preview">
                    <div class="camera-preview-wrapper">
                        <video id="cameraVideo" autoplay playsinline></video>
                    </div>
                </div>
                
                ${cameras.length > 1 ? `
                <div class="camera-simple-select">
                    <select id="cameraSelect" class="camera-select-simple">
                        ${cameras.map((camera, index) => `
                            <option value="${camera.deviceId}" ${camera.deviceId === currentDeviceId ? 'selected' : ''}>
                                ${camera.label || `Camera ${index + 1}`}
                            </option>
                        `).join('')}
                    </select>
                </div>
                ` : ''}
                
                <div class="camera-simple-actions">
                    <button class="camera-capture-btn" id="captureBtn">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                            <circle cx="12" cy="13" r="3"></circle>
                        </svg>
                        Capture
                    </button>
                    <button class="camera-cancel-btn" id="cancelCameraBtn">Cancel</button>
                </div>
            </div>
        `;
        document.body.appendChild(cameraModal);

        const video = document.getElementById('cameraVideo');
        video.srcObject = stream;
        let currentStream = stream;

        // Handle video loading
        video.addEventListener('loadedmetadata', function() {
            video.play().catch(err => {
                console.error('Error playing video:', err);
                showError('Could not start camera preview.');
                currentStream.getTracks().forEach(track => track.stop());
                document.body.removeChild(cameraModal);
            });
        });

        // Close button handler
        const closeBtn = document.getElementById('closeCameraBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                currentStream.getTracks().forEach(track => track.stop());
                document.body.removeChild(cameraModal);
            });
        }

        // Camera selection handler
        const cameraSelect = document.getElementById('cameraSelect');
        if (cameraSelect && cameras.length > 1) {
            cameraSelect.addEventListener('change', async function() {
                const selectedDeviceId = this.value;
                const newStream = await switchCamera(selectedDeviceId, currentStream);
                if (newStream) {
                    currentStream = newStream;
                }
            });
        }

        // Capture button handler (capture image)
        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.addEventListener('click', function() {
                // Capture image
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);
                
                canvas.toBlob(function(blob) {
                    // Stop camera
                    currentStream.getTracks().forEach(track => track.stop());
                    document.body.removeChild(cameraModal);
                    
                    // Handle captured image
                    const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
                    handleFileSelect(file);
                }, 'image/jpeg', 0.95);
            });
        }

        // Cancel button handler
        const cancelBtn = document.getElementById('cancelCameraBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                currentStream.getTracks().forEach(track => track.stop());
                document.body.removeChild(cameraModal);
            });
        }

        // Handle cleanup on modal close (click outside)
        cameraModal.addEventListener('click', function(e) {
            if (e.target === cameraModal) {
                currentStream.getTracks().forEach(track => track.stop());
                document.body.removeChild(cameraModal);
            }
        });

        // Close on Escape key
        const escapeHandler = function(e) {
            if (e.key === 'Escape') {
                currentStream.getTracks().forEach(track => track.stop());
                document.body.removeChild(cameraModal);
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }

    // Camera function with enhanced checks
    async function openCamera() {
        // Check if browser supports camera API
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showError('Camera API is not supported in your browser. Please use a modern browser like Chrome, Firefox, or Edge.');
            return;
        }

        // Check HTTPS/localhost requirement
        const isSecureContext = window.isSecureContext || location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1';
        if (!isSecureContext) {
            showError('Camera access requires HTTPS or localhost. Please access this site via HTTPS or localhost.');
            return;
        }

        // Request camera access - try with preferred settings first
        let stream;
        let deviceId = null;
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment' // Prefer back camera on mobile
                } 
            });
            // Get the device ID from the stream
            const track = stream.getVideoTracks()[0];
            if (track) {
                const settings = track.getSettings();
                deviceId = settings.deviceId;
            }
            await setupCameraModal(stream, deviceId);
        } catch (error) {
            // If OverconstrainedError, retry with default settings
            if (error.name === 'OverconstrainedError') {
                try {
                    console.log('Retrying with default camera settings...');
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    const track = stream.getVideoTracks()[0];
                    if (track) {
                        const settings = track.getSettings();
                        deviceId = settings.deviceId;
                    }
                    await setupCameraModal(stream, deviceId);
                    return;
                } catch (retryError) {
                    console.error('Retry failed:', retryError);
                    error = retryError; // Use retry error for final message
                }
            }
            
            // Handle all error types
            let errorMessage = 'Could not access camera. ';
            
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage += 'Camera permission was denied. Please allow camera access in your browser settings and try again.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage += 'No camera found on your device. Please connect a camera and try again.';
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                errorMessage += 'Camera is already in use by another application. Please close other applications using the camera and try again.';
            } else if (error.name === 'OverconstrainedError') {
                errorMessage += 'Camera does not support the requested settings. Please try a different camera or check your device settings.';
            } else {
                errorMessage += error.message || 'Unknown error occurred.';
            }
            
            console.error('Camera error:', error);
            showError(errorMessage);
        }
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

        // Clear history button handler
        const clearHistoryBtn = document.getElementById('clearHistoryBtn');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', function() {
                if (!confirm('Are you sure you want to clear all scan history? This action cannot be undone.')) {
                    return;
                }

                fetch('/api/clear-history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('All scan history has been cleared successfully.');
                        window.location.reload();
                    } else {
                        showError(data.error || 'Failed to clear history. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error clearing history:', error);
                    showError('An error occurred while clearing history. Please try again.');
                });
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

    // Export results function (individual scan as .txt)
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
            a.download = `fruit_scan_${scanId}.txt`;
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

    // Export history function (all scans as CSV)
    function exportHistory() {
        fetch('/api/export-history', {
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
            a.download = `fruit_scanner_history_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            showError('Could not export history.');
            console.error('Error:', error);
        });
    }

    // Export history button handler
    const exportHistoryBtn = document.getElementById('exportHistoryBtn');
    if (exportHistoryBtn) {
        exportHistoryBtn.addEventListener('click', function() {
            exportHistory();
        });
    }

    // Display results on the page (right side)
    function displayResultsOnPage(scanId, resultsData) {
        const resultsContent = document.getElementById('resultsContent');
        
        if (resultsContent && resultsData) {
            // Build results HTML
            const fruits = resultsData.fruits || [];
            let resultsHTML = '';
                        
            // Add fruits list
            if (fruits.length > 0) {
                resultsHTML += `
                    <div>
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #2c5530; margin-bottom: 12px;">Detected Fruits</h4>
                        <div style="max-height: 300px; overflow-y: auto; margin-bottom: 16px;">
                            <div style="display: grid; grid-template-columns: 2fr 1.5fr 1fr; gap: 12px; padding: 10px 12px; background: #f8f9fa; border-radius: 4px; margin-bottom: 8px; font-size: 0.75rem; font-weight: 600; color: #495057; text-transform: uppercase; letter-spacing: 0.5px;">
                                <div>Fruit Type</div>
                                <div>Ripeness</div>
                                <div style="text-align: right;">Confidence</div>
                            </div>
                `;
                
                // Store fruits data for modal
                window.currentFruitsData = fruits;
                window.currentScanId = scanId;
                
                fruits.forEach((fruit, index) => {
                    let displayType = fruit.type || 'Unknown';
                    const ripeness = fruit.ripeness || 'Unknown';
                    const confidence = ((fruit.confidence || 0) * 100).toFixed(1);
                    
                    // Remove ripeness keywords from fruit type name
                    const ripenessKeywords = ['ripe', 'unripe', 'overripe', 'half-ripe', 'half ripe'];
                    ripenessKeywords.forEach(keyword => {
                        // Remove keyword at the start, end, or middle of the string
                        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
                        displayType = displayType.replace(regex, '').trim();
                        // Clean up extra spaces
                        displayType = displayType.replace(/\s+/g, ' ').trim();
                    });
                    
                    // Determine badge color
                    let badgeColor = '#6c757d';
                    if (ripeness.toLowerCase() === 'ripe') badgeColor = '#ffc107';
                    else if (ripeness.toLowerCase() === 'unripe') badgeColor = '#17a2b8';
                    else if (ripeness.toLowerCase() === 'overripe') badgeColor = '#dc3545';
                    
                    resultsHTML += `
                        <div style="display: grid; grid-template-columns: 2fr 1.5fr 1fr; gap: 12px; align-items: center; padding: 10px 12px; border-bottom: 1px solid #e9ecef; font-size: 0.8125rem;">
                            <div>
                                <strong style="color: #495057;">${displayType}</strong>
                            </div>
                            <div>
                                <span style="display: inline-block; padding: 3px 10px; border-radius: 4px; background: ${badgeColor}; color: white; font-size: 0.75rem; font-weight: 500;">${ripeness}</span>
                            </div>
                            <div style="color: #6c757d; font-weight: 500; text-align: right;">${confidence}%</div>
                        </div>
                    `;
                });
                
                resultsHTML += `
                        </div>
                    </div>
                `;
            } else {
                resultsHTML = `
                    <div style="text-align: center; padding: 20px; color: #6c757d;">
                        <p style="font-size: 0.875rem; margin: 0;">No fruits detected in this scan.</p>
                    </div>
                `;
            }
            
            // Add action buttons
            resultsHTML += `
                <div style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px;">
                    <button class="btn btn-primary" onclick="showFullResultsModal()" style="width: 100%; text-align: center; font-size: 0.875rem; padding: 8px;">View Full Results</button>
                    <button class="btn btn-secondary" onclick="clearResults()" style="width: 100%; font-size: 0.875rem; padding: 8px;">Clear Results</button>
                </div>
            `;
            
            resultsContent.innerHTML = resultsHTML;
        }
    }

    // Clear results function
    window.clearResults = function() {
        const resultsContent = document.getElementById('resultsContent');
        
        if (resultsContent) {
            resultsContent.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: #6c757d;">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin: 0 auto 16px; opacity: 0.5;">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                    <p style="font-size: 0.875rem; margin-bottom: 8px; font-weight: 500; color: #495057;">No scan performed yet</p>
                    <p style="font-size: 0.8125rem; margin: 0; opacity: 0.8;">Upload an image and click "Scan Fruit" to see results here</p>
                </div>
            `;
        }
    };

    // Show full results modal with YOLO/NIR weighted confidence
    window.showFullResultsModal = function() {
        const fruits = window.currentFruitsData || [];
        const scanId = window.currentScanId || '';
        
        if (!fruits || fruits.length === 0) {
            alert('No results to display');
            return;
        }
        // Create modal overlay
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';
        modalOverlay.id = 'fullResultsModal';
        modalOverlay.style.display = 'flex';
        
        let modalHTML = `
            <div class="modal-content" style="max-width: 800px;">
                <div class="modal-header">
                    <h2>Full Results - Fusion Analysis</h2>
                    <button class="modal-close" onclick="closeFullResultsModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="fusion-info">
                        <p class="fusion-description">
                            The freshness score is computed using weighted averaging of YOLO and Felix (NIR Scanner) confidence scores:
                        </p>
                        <div class="weight-formula">
                            <strong>Freshness Score = (YOLO Confidence × 0.7) + (Felix Confidence × 0.3)</strong>
                        </div>
                    </div>
                    <div class="fruits-analysis">
        `;
        
        fruits.forEach((fruit, index) => {
            let displayType = fruit.type || 'Unknown';
            const ripeness = fruit.ripeness || 'Unknown';
            
            // Remove ripeness keywords from fruit type name
            const ripenessKeywords = ['ripe', 'unripe', 'overripe', 'half-ripe', 'half ripe'];
            ripenessKeywords.forEach(keyword => {
                const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
                displayType = displayType.replace(regex, '').trim();
                displayType = displayType.replace(/\s+/g, ' ').trim();
            });
            
            const yoloConfidence = (fruit.yolo_confidence || fruit.confidence || 0) * 100;
            const nirConfidence = (fruit.nir_confidence || 0) * 100;
            const yoloWeight = 0.7;
            const nirWeight = 0.3;
            const yoloContribution = yoloConfidence * yoloWeight;
            const nirContribution = nirConfidence * nirWeight;
            const finalScore = yoloContribution + nirContribution;
            
            modalHTML += `
                <div class="fruit-analysis-card">
                    <div class="fruit-header">
                        <h3>${displayType}</h3>
                        <span class="final-score">Final Score: ${finalScore.toFixed(1)}%</span>
                    </div>
                    <div class="computation-details">
                        <div class="computation-row">
                            <div class="computation-label">YOLO Confidence:</div>
                            <div class="computation-value">${yoloConfidence.toFixed(2)}%</div>
                            <div class="computation-weight">Weight: ${yoloWeight}</div>
                            <div class="computation-result">= ${yoloContribution.toFixed(2)}%</div>
                        </div>
                        <div class="computation-row">
                            <div class="computation-label">Felix (NIR) Confidence:</div>
                            <div class="computation-value">${nirConfidence.toFixed(2)}%</div>
                            <div class="computation-weight">Weight: ${nirWeight}</div>
                            <div class="computation-result">= ${nirContribution.toFixed(2)}%</div>
                        </div>
                        <div class="computation-divider"></div>
                        <div class="computation-row computation-final">
                            <div class="computation-label">Freshness Score:</div>
                            <div class="computation-value-final">${finalScore.toFixed(2)}%</div>
                        </div>
                    </div>
                    <div class="fruit-metadata">
                        <span class="metadata-item">Ripeness: <strong>${ripeness}</strong></span>
                    </div>
                </div>
            `;
        });
        
        modalHTML += `
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeFullResultsModal()">Close</button>
                </div>
            </div>
        `;
        
        modalOverlay.innerHTML = modalHTML;
        document.body.appendChild(modalOverlay);
        document.body.style.overflow = 'hidden';
        
        // Close on overlay click
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                closeFullResultsModal();
            }
        });
    };

    // Close full results modal
    window.closeFullResultsModal = function() {
        const modal = document.getElementById('fullResultsModal');
        if (modal) {
            modal.remove();
            document.body.style.overflow = '';
        }
    };

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('fullResultsModal');
            if (modal && modal.style.display === 'flex') {
                closeFullResultsModal();
            }
        }
    });
});

// Add camera modal styles dynamically - Fruit Scanner themed design
const style = document.createElement('style');
style.textContent = `
    .camera-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(4px);
        z-index: 2000;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        animation: fadeIn 0.2s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .camera-simple-panel {
        background: white;
        border-radius: 8px;
        width: 100%;
        max-width: 650px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        overflow: hidden;
        animation: slideUp 0.3s ease-out;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .camera-simple-header {
        padding: 24px 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #e9ecef;
        background: white;
    }
    
    .camera-simple-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c5530;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .camera-simple-close {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        color: #6c757d;
        font-size: 24px;
        line-height: 1;
        cursor: pointer;
        padding: 0;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        border-radius: 6px;
    }
    
    .camera-simple-close:hover {
        color: #2c5530;
        background: #e9ecef;
        border-color: #2c5530;
    }
    
    .camera-simple-preview {
        padding: 32px;
        background: #f8f9fa;
    }
    
    .camera-preview-wrapper {
        position: relative;
        width: 100%;
        background: #000;
        border-radius: 6px;
        overflow: hidden;
        aspect-ratio: 4 / 3;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    #cameraVideo {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    
    .camera-simple-select {
        padding: 0 32px 24px;
        background: #f8f9fa;
    }
    
    .camera-select-simple {
        width: 100%;
        padding: 10px 16px;
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        color: #495057;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
    }
    
    .camera-select-simple:hover {
        border-color: #2c5530;
        background: white;
    }
    
    .camera-select-simple:focus {
        outline: none;
        border-color: #2c5530;
        box-shadow: 0 0 0 3px rgba(44, 85, 48, 0.1);
    }
    
    .camera-select-simple option {
        background: white;
        color: #495057;
        padding: 8px;
    }
    
    .camera-simple-actions {
        padding: 24px 32px;
        display: flex;
        gap: 12px;
        justify-content: center;
        background: white;
        border-top: 1px solid #e9ecef;
    }
    
    .camera-capture-btn {
        flex: 1;
        padding: 12px 24px;
        background: #2c5530;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        min-height: 44px;
    }
    
    .camera-capture-btn:hover {
        background: #1e3d22;
        box-shadow: 0 2px 6px rgba(44, 85, 48, 0.25);
    }
    
    .camera-capture-btn:active {
        transform: translateY(1px);
    }
    
    .camera-capture-btn svg {
        width: 18px;
        height: 18px;
    }
    
    .camera-cancel-btn {
        padding: 12px 24px;
        background: white;
        color: #2c5530;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: inherit;
        min-height: 44px;
    }
    
    .camera-cancel-btn:hover {
        background: #f8f9fa;
        border-color: #2c5530;
        color: #2c5530;
    }
    
    @media (max-width: 600px) {
        .camera-simple-panel {
            max-width: 100%;
            border-radius: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .camera-modal {
            padding: 0;
        }
        
        .camera-simple-header {
            padding: 20px;
        }
        
        .camera-simple-preview {
            padding: 20px;
            flex: 1;
            display: flex;
            align-items: center;
        }
        
        .camera-simple-select {
            padding: 0 20px 20px;
        }
        
        .camera-simple-actions {
            padding: 20px;
            flex-direction: column;
        }
        
        .camera-capture-btn,
        .camera-cancel-btn {
            width: 100%;
        }
    }
`;
document.head.appendChild(style);

