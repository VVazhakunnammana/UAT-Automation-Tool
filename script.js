class ExcelUploadApp {
    constructor() {
        this.selectedFile = null;
        this.fileUploaded = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.clearUploads(); // Clear uploads folder on page load/refresh
        this.loadTemplateFiles(); // Load available template files
        this.loadOutputFiles(); // Load available output files
        this.updateStatus('Ready to upload file...');
    }

    setupEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const runTestBtn = document.getElementById('runTestBtn');

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files[0]);
        });

        // Drag and drop
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && this.isValidExcelFile(file)) {
                this.handleFileSelection(file);
            } else {
                this.showError('Please select a valid Excel file (.xlsx or .xls)');
            }
        });

        // Button clicks
        uploadBtn.addEventListener('click', () => {
            this.uploadFile();
        });

        runTestBtn.addEventListener('click', () => {
            this.runTests();
        });

        // Download functionality event listeners
        // const generateOutputBtn = document.getElementById('generateOutputBtn');
        const refreshFilesBtn = document.getElementById('refreshFilesBtn');
        const refreshTemplatesBtn = document.getElementById('refreshTemplatesBtn');

        // generateOutputBtn.addEventListener('click', () => {
        //     this.generateSampleOutput();
        // });

        refreshFilesBtn.addEventListener('click', () => {
            this.loadOutputFiles();
        });

        refreshTemplatesBtn.addEventListener('click', () => {
            this.loadTemplateFiles();
        });
    }

    handleFileSelection(file) {
        if (!file) return;

        if (this.isValidExcelFile(file)) {
            this.selectedFile = file;
            this.showFileInfo(file);
            this.enableUploadButton();
            this.updateStatus('File selected. Ready to upload.');
        } else {
            this.showError('Please select a valid Excel file (.xlsx or .xls)');
        }
    }

    isValidExcelFile(file) {
        const validTypes = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
            'application/vnd.ms-excel' // .xls
        ];
        return validTypes.includes(file.type) || 
               file.name.toLowerCase().endsWith('.xlsx') || 
               file.name.toLowerCase().endsWith('.xls');
    }

    showFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        fileName.textContent = file.name;
        fileSize.textContent = `Size: ${this.formatFileSize(file.size)}`;
        fileInfo.style.display = 'block';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    enableUploadButton() {
        document.getElementById('uploadBtn').disabled = false;
    }

    async uploadFile() {
        if (!this.selectedFile) {
            this.showError('No file selected');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        this.updateStatus('Uploading file...', 'processing');
        this.showProgress(0);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.fileUploaded = true;
                this.updateStatus('File uploaded successfully!', 'success');
                this.enableTestButton();
                this.hideProgress();
                
                // Show file preview if available
                if (result.preview) {
                    this.showFilePreview(result.preview);
                }
            } else {
                const error = await response.json();
                this.showError(`Upload failed: ${error.error || 'Unknown error'}`);
            }
        } catch (error) {
            this.showError(`Upload failed: ${error.message}`);
        }
    }

    enableTestButton() {
        document.getElementById('runTestBtn').disabled = false;
        //document.getElementById('generateOutputBtn').disabled = false;
        this.showDownloadSection();
        this.loadOutputFiles();
    }

    async runTests() {
        if (!this.fileUploaded) {
            this.showError('Please upload a file first');
            return;
        }

        this.updateStatus('Running pytest scripts...', 'processing');
        this.showProgress(0);
        this.showOutputPanel();

        try {
            const response = await fetch('/run-tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.updateStatus('Tests completed!', result.success ? 'success' : 'error');
                this.showTestResults(result);
                this.hideProgress();
            } else {
                const error = await response.json();
                this.showError(`Test execution failed: ${error.error || 'Unknown error'}`);
            }
        } catch (error) {
            this.showError(`Test execution failed: ${error.message}`);
        }
    }

    showTestResults(result) {
        const outputContent = document.getElementById('outputContent');
        
        let output = `=== Test Execution Results ===\n\n`;
        output += `Status: ${result.success ? 'PASSED' : 'FAILED'}\n`;
        output += `Exit Code: ${result.exit_code}\n`;
        output += `Duration: ${result.duration}s\n\n`;
        output += `=== STDOUT ===\n${result.stdout}\n\n`;
        
        if (result.stderr) {
            output += `=== STDERR ===\n${result.stderr}\n\n`;
        }
        
        if (result.test_summary) {
            output += `=== Summary ===\n${result.test_summary}`;
        }

        outputContent.textContent = output;
    }

    showOutputPanel() {
        document.getElementById('outputPanel').style.display = 'block';
    }

    showFilePreview(preview) {
        // Could be extended to show Excel data preview
        console.log('File preview:', preview);
    }

    updateStatus(message, type = 'info') {
        const statusContent = document.getElementById('statusContent');
        statusContent.textContent = message;
        statusContent.className = `status-content ${type}`;
    }

    showError(message) {
        this.updateStatus(message, 'error');
        this.hideProgress();
    }

    showProgress(percent) {
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        
        progressBar.style.display = 'block';
        progressFill.style.width = `${percent}%`;
        
        // Simulate progress for demo purposes
        if (percent < 100) {
            setTimeout(() => {
                this.showProgress(Math.min(percent + 20, 100));
            }, 200);
        }
    }

    hideProgress() {
        const progressBar = document.getElementById('progressBar');
        progressBar.style.display = 'none';
    }

    // Download functionality methods
    showDownloadSection() {
        document.getElementById('downloadSection').style.display = 'block';
    }

    async loadOutputFiles() {
        const filesList = document.getElementById('filesList');
        filesList.innerHTML = '<p class="loading-text">Loading files...</p>';

        try {
            const response = await fetch('/list-output-files');
            if (response.ok) {
                const data = await response.json();
                this.displayOutputFiles(data.files);
            } else {
                filesList.innerHTML = '<p class="no-files-text">Failed to load files</p>';
            }
        } catch (error) {
            console.error('Failed to load output files:', error);
            filesList.innerHTML = '<p class="no-files-text">Error loading files</p>';
        }
    }

    displayOutputFiles(files) {
        const filesList = document.getElementById('filesList');
        
        if (files.length === 0) {
            filesList.innerHTML = '<p class="no-files-text">No output files available. Generate some results first!</p>';
            return;
        }

        filesList.innerHTML = files.map(file => `
            <div class="file-item">
                <div class="file-info-left">
                    <div class="file-name">
                        <span class="file-icon ${this.getFileIcon(file.filename)}"></span>
                        ${file.filename}
                    </div>
                    <div class="file-details">
                        <div class="file-size">📏 ${this.formatFileSize(file.size)}</div>
                        <div class="file-date">📅 ${file.modified}</div>
                    </div>
                </div>
                <button class="download-btn" onclick="app.downloadFile('${file.filename}')">
                    ⬇️ Download
                </button>
            </div>
        `).join('');
    }

    getFileIcon(filename) {
        const ext = filename.toLowerCase().split('.').pop();
        switch (ext) {
            case 'xlsx':
            case 'xls':
                return 'excel-icon';
            case 'csv':
                return 'csv-icon';
            case 'txt':
                return 'text-icon';
            case 'json':
                return 'json-icon';
            default:
                return 'default-icon';
        }
    }

    async downloadFile(filename) {
        try {
            const response = await fetch(`/download-output/${encodeURIComponent(filename)}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.updateStatus(`Downloaded: ${filename}`, 'success');
            } else {
                this.showError(`Failed to download ${filename}`);
            }
        } catch (error) {
            this.showError(`Download error: ${error.message}`);
        }
    }

    async clearUploads() {
        try {
            const response = await fetch('/clear-uploads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                console.log(`Cleared uploads: ${result.message}`);
                // Reset file state
                this.selectedFile = null;
                this.fileUploaded = false;
                
                // Hide file info and reset UI
                const fileInfo = document.getElementById('fileInfo');
                if (fileInfo) fileInfo.style.display = 'none';
                
                // Reset buttons
                const uploadBtn = document.getElementById('uploadBtn');
                const runTestBtn = document.getElementById('runTestBtn');
                if (uploadBtn) uploadBtn.disabled = true;
                if (runTestBtn) runTestBtn.disabled = true;
                
                // Reset file input
                const fileInput = document.getElementById('fileInput');
                if (fileInput) fileInput.value = '';
                
            } else {
                console.error('Failed to clear uploads folder');
            }
        } catch (error) {
            console.error(`Error clearing uploads: ${error.message}`);
        }
    }

    async loadTemplateFiles() {
        try {
            const response = await fetch('/list-template-files');
            if (response.ok) {
                const result = await response.json();
                this.displayTemplateFiles(result.files);
            } else {
                document.getElementById('templatesList').innerHTML = 
                    '<p class="no-files-text">Failed to load template files</p>';
            }
        } catch (error) {
            document.getElementById('templatesList').innerHTML = 
                '<p class="no-files-text">Error loading template files</p>';
        }
    }

    displayTemplateFiles(files) {
        const templatesList = document.getElementById('templatesList');
        
        if (!files || files.length === 0) {
            templatesList.innerHTML = '<p class="no-files-text">No template files available</p>';
            return;
        }

        const filesHtml = files.map(file => `
            <div class="template-item">
                <div class="template-info">
                    <div class="template-name">
                        <span class="file-icon excel-icon"></span>
                        ${file.name}
                    </div>
                </div>
                <button class="template-download-btn" onclick="app.downloadTemplate('${file.name}')">
                    ⬇️ Download
                </button>
            </div>
        `).join('');

        templatesList.innerHTML = filesHtml;
    }

    async downloadTemplate(filename) {
        try {
            const response = await fetch(`/download-template/${encodeURIComponent(filename)}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.updateStatus(`Downloaded template: ${filename}`, 'success');
            } else {
                this.showError(`Failed to download template ${filename}`);
            }
        } catch (error) {
            this.showError(`Template download error: ${error.message}`);
        }
    }

    // async generateSampleOutput() {
    //     if (!this.fileUploaded) {
    //         this.showError('Please upload a file first');
    //         return;
    //     }

    //     this.updateStatus('Generating sample output...', 'processing');
        
    //     try {
    //         const response = await fetch('/create-sample-output', {
    //             method: 'POST',
    //             headers: {
    //                 'Content-Type': 'application/json'
    //             }
    //         });

    //         if (response.ok) {
    //             const result = await response.json();
    //             this.updateStatus('Sample output generated successfully!', 'success');
    //             this.loadOutputFiles(); // Refresh the files list
    //         } else {
    //             const error = await response.json();
    //             this.showError(`Failed to generate output: ${error.error || 'Unknown error'}`);
    //         }
    //     } catch (error) {
    //         this.showError(`Output generation failed: ${error.message}`);
    //     }
    // }
}

// Initialize the app when the DOM is loaded
let app; // Global app instance
document.addEventListener('DOMContentLoaded', () => {
    app = new ExcelUploadApp();
});

// Utility functions for potential enhancements
const utils = {
    // Function to validate Excel file content
    async validateExcelContent(file) {
        // This could be enhanced to read and validate Excel content on the client side
        return true;
    },

    // Function to show notifications
    showNotification(message, type = 'info') {
        // Could implement toast notifications
        console.log(`${type.toUpperCase()}: ${message}`);
    },

    // Function to download test results
    downloadResults(results) {
        const blob = new Blob([results], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'test_results.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
};
