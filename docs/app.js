/**
 * RunLog AI - Web Application
 * Handles file uploads, processing, and downloads
 */

class RunLogApp {
    constructor() {
        this.parser = new RunLogParser();
        this.files = [];
        this.processedData = null;

        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.elements = {
            uploadBox: document.getElementById('uploadBox'),
            fileInput: document.getElementById('fileInput'),
            browseBtn: document.getElementById('browseBtn'),
            helpBtn: document.getElementById('helpBtn'),
            filesSection: document.getElementById('filesSection'),
            filesList: document.getElementById('filesList'),
            fileCount: document.getElementById('fileCount'),
            clearAllBtn: document.getElementById('clearAllBtn'),
            optionsSection: document.getElementById('optionsSection'),
            chunkSize: document.getElementById('chunkSize'),
            includeGPS: document.getElementById('includeGPS'),
            processBtn: document.getElementById('processBtn'),
            progressSection: document.getElementById('progressSection'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText'),
            resultsSection: document.getElementById('resultsSection'),
            statsGrid: document.getElementById('statsGrid'),
            downloadLinks: document.getElementById('downloadLinks'),
            helpModal: document.getElementById('helpModal'),
            modalClose: document.getElementById('modalClose')
        };
    }

    attachEventListeners() {
        // Browse button
        this.elements.browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.elements.fileInput.click();
        });

        // File input change - FIXED: Reset value after reading to allow re-selecting
        this.elements.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
                // Reset input value to allow selecting the same file again
                e.target.value = '';
            }
        });

        // Clear all button
        this.elements.clearAllBtn.addEventListener('click', () => {
            this.clearAllFiles();
        });

        // Drag and drop
        this.elements.uploadBox.addEventListener('click', () => {
            this.elements.fileInput.click();
        });

        this.elements.uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.elements.uploadBox.classList.add('drag-over');
        });

        this.elements.uploadBox.addEventListener('dragleave', () => {
            this.elements.uploadBox.classList.remove('drag-over');
        });

        this.elements.uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            this.elements.uploadBox.classList.remove('drag-over');
            this.handleFiles(e.dataTransfer.files);
        });

        // Process button
        this.elements.processBtn.addEventListener('click', () => {
            this.processFiles();
        });

        // Help modal
        this.elements.helpBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the upload box click
            this.openModal();
        });

        this.elements.modalClose.addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal when clicking outside
        this.elements.helpModal.addEventListener('click', (e) => {
            if (e.target === this.elements.helpModal) {
                this.closeModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.elements.helpModal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }

    openModal() {
        this.elements.helpModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        this.elements.helpModal.classList.remove('show');
        document.body.style.overflow = '';
    }

    handleFiles(fileList) {
        const newFiles = Array.from(fileList).filter(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            return ['fit', 'tcx', 'csv'].includes(ext);
        });

        if (newFiles.length === 0) {
            alert('Please upload FIT, TCX, or CSV files.');
            return;
        }

        console.log(`Adding ${newFiles.length} new files:`, newFiles.map(f => f.name));
        this.files = [...this.files, ...newFiles];
        this.updateFilesDisplay();
        this.elements.filesSection.style.display = 'block';
        this.elements.optionsSection.style.display = 'block';
    }

    updateFilesDisplay() {
        // Update file count
        this.elements.fileCount.textContent = this.files.length;

        // Group files by date
        const filesByDate = this.groupFilesByDate(this.files);

        this.elements.filesList.innerHTML = '';

        Object.entries(filesByDate).forEach(([date, files]) => {
            const dateGroup = document.createElement('div');
            dateGroup.style.marginBottom = '0.75rem';

            const dateHeader = document.createElement('div');
            dateHeader.style.fontWeight = '600';
            dateHeader.style.fontSize = '0.8125rem';
            dateHeader.style.padding = '0.375rem 0.5rem';
            dateHeader.style.background = '#f1f5f9';
            dateHeader.style.borderRadius = '0.375rem';
            dateHeader.style.marginBottom = '0.375rem';
            dateHeader.style.color = '#64748b';
            dateHeader.textContent = `📅 ${this.formatDate(date)} (${files.length} file${files.length > 1 ? 's' : ''})`;

            dateGroup.appendChild(dateHeader);

            files.forEach(file => {
                const fileItem = this.createFileItem(file);
                dateGroup.appendChild(fileItem);
            });

            this.elements.filesList.appendChild(dateGroup);
        });
    }

    clearAllFiles() {
        this.files = [];
        this.elements.filesSection.style.display = 'none';
        this.elements.optionsSection.style.display = 'none';
        this.elements.resultsSection.style.display = 'none';
    }

    groupFilesByDate(files) {
        const groups = {};

        files.forEach(file => {
            const date = this.extractDateFromFilename(file.name);
            if (!groups[date]) {
                groups[date] = [];
            }
            groups[date].push(file);
        });

        return groups;
    }

    extractDateFromFilename(fileName) {
        // Try to extract date pattern like YYYYMMDD or YYYY-MM-DD
        // Look for patterns at start of filename or after slash/underscore
        const patterns = [
            /^(\d{4})[-_]?(\d{2})[-_]?(\d{2})/,  // Start of filename: 20251202 or 2025-12-02
            /[\/\\](\d{4})[-_]?(\d{2})[-_]?(\d{2})/, // After slash: /20251202/
            /_(\d{4})[-_]?(\d{2})[-_]?(\d{2})/,  // After underscore: _20251202_
        ];

        for (const pattern of patterns) {
            const match = fileName.match(pattern);
            if (match) {
                const year = parseInt(match[1]);
                const month = parseInt(match[2]);
                const day = parseInt(match[3]);

                // Validate it's a reasonable date
                if (year >= 2000 && year <= 2100 && month >= 1 && month <= 12 && day >= 1 && day <= 31) {
                    const extractedDate = `${match[1]}${match[2]}${match[3]}`;
                    console.log(`Extracted date "${extractedDate}" from file "${fileName}"`);
                    return extractedDate;
                }
            }
        }

        // If no valid date found, use 'unknown'
        console.log(`No valid date found in filename "${fileName}", using "unknown"`);
        return 'unknown';
    }

    formatDate(dateStr) {
        if (dateStr === 'unknown') return 'Unknown Date';

        // Ensure we have exactly 8 digits
        if (dateStr.length !== 8) return 'Invalid Date';

        const year = dateStr.substring(0, 4);
        const month = dateStr.substring(4, 6);
        const day = dateStr.substring(6, 8);

        return `${year}-${month}-${day}`;
    }

    createFileItem(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const ext = file.name.split('.').pop().toUpperCase();

        fileItem.innerHTML = `
            <div class="file-info">
                <div class="file-icon">${ext}</div>
                <div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            </div>
            <button class="file-remove" onclick="app.removeFile('${file.name}')">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        return fileItem;
    }

    removeFile(fileName) {
        this.files = this.files.filter(f => f.name !== fileName);
        this.updateFilesDisplay();

        if (this.files.length === 0) {
            this.elements.filesSection.style.display = 'none';
            this.elements.optionsSection.style.display = 'none';
        }
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    async processFiles() {
        this.elements.optionsSection.style.display = 'none';
        this.elements.progressSection.style.display = 'block';
        this.elements.resultsSection.style.display = 'none';

        const chunkSize = parseInt(this.elements.chunkSize.value) || 5;
        const includeGPS = this.elements.includeGPS.checked;

        try {
            // Step 1: Group files by base filename (without extension)
            const fileGroups = {};
            this.files.forEach(file => {
                const baseName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
                if (!fileGroups[baseName]) {
                    fileGroups[baseName] = [];
                }
                fileGroups[baseName].push(file);
            });

            console.log('Files grouped by base filename:', Object.keys(fileGroups).map(key => ({
                baseName: key,
                files: fileGroups[key].map(f => f.name)
            })));

            // Step 2: Parse each file group and extract timestamp from TCX (if available)
            const parsedGroups = [];
            let processedFiles = 0;
            const totalFiles = this.files.length;

            for (const [baseName, files] of Object.entries(fileGroups)) {
                const group = {
                    baseName: baseName,
                    files: [],
                    timestampKey: null
                };

                // Parse all files in this group
                for (const file of files) {
                    const ext = file.name.split('.').pop().toLowerCase();
                    const content = await this.readFile(file, ext);

                    let parsed = null;
                    if (ext === 'csv') {
                        parsed = this.parser.parseCSV(content, file.name);
                    } else if (ext === 'tcx') {
                        parsed = this.parser.parseTCX(content, file.name);
                    } else if (ext === 'fit') {
                        parsed = this.parser.parseFIT(content, file.name);
                    }

                    if (parsed) {
                        group.files.push({
                            file: file,
                            parsed: parsed,
                            ext: ext
                        });

                        // Extract timestamp from TCX activity_id if available
                        if (parsed.sources?.tcx?.data?.activity_id) {
                            group.timestampKey = parsed.sources.tcx.data.activity_id;
                            console.log(`Using TCX timestamp for group ${baseName}: ${group.timestampKey}`);
                        }
                    }

                    processedFiles++;
                    this.updateProgress((processedFiles / totalFiles) * 100, `Processing ${file.name}...`);
                }

                // If no TCX timestamp found, use the date from first file
                if (!group.timestampKey && group.files.length > 0) {
                    group.timestampKey = group.files[0].parsed.date;
                    console.log(`No TCX timestamp for group ${baseName}, using date: ${group.timestampKey}`);
                }

                if (group.files.length > 0) {
                    parsedGroups.push(group);
                }
            }

            console.log('Parsed groups with timestamps:', parsedGroups.map(g => ({
                baseName: g.baseName,
                timestamp: g.timestampKey,
                fileCount: g.files.length,
                files: g.files.map(pf => pf.file.name)
            })));

            // Step 3: Create activities from parsed groups
            const activities = [];
            for (const group of parsedGroups) {
                const activity = {
                    date: group.files[0].parsed.date,
                    metadata: {},
                    sources: {}
                };

                // Merge all sources from this group
                for (const pf of group.files) {
                    if (pf.ext === 'csv' && pf.parsed.sources?.csv) {
                        activity.sources.csv = pf.parsed.sources.csv;
                        if (pf.parsed.sources.csv.data.summary) {
                            activity.summary = pf.parsed.sources.csv.data.summary;
                        }
                    } else if (pf.ext === 'tcx' && pf.parsed.sources?.tcx) {
                        activity.sources.tcx = pf.parsed.sources.tcx;
                        if (!includeGPS && pf.parsed.sources.tcx.data.trackpoints) {
                            activity.sources.tcx.data.trackpoints = [];
                        }
                    } else if (pf.ext === 'fit' && pf.parsed.sources?.fit) {
                        activity.sources.fit = pf.parsed.sources.fit;
                    }
                }

                // Only add activity if it has at least one source
                if (Object.keys(activity.sources).length > 0) {
                    activities.push(activity);
                }
            }

            console.log('Total activities created:', activities.length);
            console.log('Activities:', activities);

            this.updateProgress(100, 'Creating training log...');

            // Create training log with chunking
            this.processedData = this.parser.createTrainingLog(activities, chunkSize);

            console.log('Processed data:', this.processedData);

            // Show results
            this.showResults();

        } catch (error) {
            console.error('Error processing files:', error);
            alert('Error processing files. Please check the console for details.');
            this.elements.progressSection.style.display = 'none';
            this.elements.optionsSection.style.display = 'block';
        }
    }

    async readFile(file, ext) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                if (ext === 'fit') {
                    resolve(e.target.result); // ArrayBuffer for FIT
                } else {
                    resolve(e.target.result); // Text for CSV/TCX
                }
            };

            reader.onerror = reject;

            if (ext === 'fit') {
                reader.readAsArrayBuffer(file);
            } else {
                reader.readAsText(file);
            }
        });
    }

    updateProgress(percent, text) {
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = text;
    }

    showResults() {
        this.elements.progressSection.style.display = 'none';
        this.elements.resultsSection.style.display = 'block';

        // Show statistics
        const stats = this.processedData.statistics || this.processedData.data?.statistics;

        this.elements.statsGrid.innerHTML = '';

        if (stats) {
            this.addStatCard('Total Activities',
                this.processedData.type === 'single'
                    ? this.processedData.data.metadata.total_activities
                    : this.processedData.index.data.metadata.total_activities
            );
            this.addStatCard('Total Distance', `${stats.total_distance_km} km`);
            this.addStatCard('Total Time', stats.total_time_formatted);
            this.addStatCard('Avg Distance', `${stats.average_distance_per_run} km/run`);

            if (this.processedData.type === 'chunked') {
                this.addStatCard('Chunks Created', this.processedData.chunks.length);
            }
        }

        // Create download links
        this.createDownloadLinks();
    }

    addStatCard(label, value) {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.innerHTML = `
            <div class="stat-label">${label}</div>
            <div class="stat-value">${value}</div>
        `;
        this.elements.statsGrid.appendChild(card);
    }

    createDownloadLinks() {
        this.elements.downloadLinks.innerHTML = '';

        if (this.processedData.type === 'single') {
            // Single file download
            this.addDownloadLink(
                'training_log.json',
                this.processedData.data,
                'Complete Training Log'
            );
        } else {
            // Index file
            this.addDownloadLink(
                this.processedData.index.fileName,
                this.processedData.index.data,
                'Index File (Overview)'
            );

            // Chunk files
            this.processedData.chunks.forEach((chunk, idx) => {
                this.addDownloadLink(
                    chunk.fileName,
                    chunk.data,
                    `Chunk ${idx + 1} (${chunk.info.activity_count} activities)`
                );
            });
        }
    }

    addDownloadLink(fileName, data, description) {
        const link = document.createElement('a');
        link.className = 'download-link';
        link.href = '#';

        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        link.onclick = (e) => {
            e.preventDefault();
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            a.click();
        };

        const fileSize = new Blob([jsonStr]).size;

        link.innerHTML = `
            <div class="download-info">
                <div class="download-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                </div>
                <div>
                    <div style="font-weight: 500;">${fileName}</div>
                    <div style="font-size: 0.875rem; color: var(--text-light);">
                        ${description} • ${this.formatFileSize(fileSize)}
                    </div>
                </div>
            </div>
            <svg class="download-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
        `;

        this.elements.downloadLinks.appendChild(link);
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new RunLogApp();
});
