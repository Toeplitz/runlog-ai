/**
 * RunLog AI - Client-Side Parser
 * Parses FIT, TCX, and CSV running watch data files
 */

class RunLogParser {
    constructor() {
        this.activities = [];
    }

    /**
     * Parse CSV file (Coros format)
     */
    parseCSV(content, fileName) {
        const lines = content.split('\n').map(l => l.trim()).filter(l => l);
        if (lines.length < 2) return null;

        const activity = {
            date: this.extractDateFromFilename(fileName),
            metadata: {},
            sources: {
                csv: {
                    file: fileName,
                    data: {
                        splits: [],
                        summary: {}
                    }
                }
            }
        };

        // Parse splits and summary
        const header = lines[0].split(',');

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            const row = {};

            header.forEach((key, idx) => {
                row[key.trim()] = values[idx]?.trim() || '';
            });

            if (row.Split?.toLowerCase() === 'summary') {
                activity.sources.csv.data.summary = this.cleanCSVRow(row);
            } else if (row.Split && row.Split.toLowerCase() !== 'split') {
                activity.sources.csv.data.splits.push(this.cleanCSVRow(row));
            }
        }

        return activity;
    }

    /**
     * Parse TCX file
     */
    parseTCX(content, fileName) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(content, 'text/xml');

        // Check for parsing errors
        if (xmlDoc.querySelector('parsererror')) {
            console.error('Error parsing TCX file:', fileName);
            return null;
        }

        // Get activity type and ID first to extract date
        let activityDate = null;
        const activityElem = xmlDoc.querySelector('Activity');
        if (activityElem) {
            const idElem = activityElem.querySelector('Id');
            if (idElem) {
                // Activity ID is typically an ISO timestamp like "2025-01-15T10:30:00.000Z"
                const activityId = idElem.textContent;
                try {
                    const date = new Date(activityId);
                    if (!isNaN(date.getTime())) {
                        activityDate = date.toISOString().split('T')[0].replace(/-/g, '');
                    }
                } catch (e) {
                    console.warn('Could not parse date from TCX activity ID:', activityId);
                }
            }
        }

        // Fallback to filename if no date in content
        if (!activityDate) {
            activityDate = this.extractDateFromFilename(fileName);
        }

        const activity = {
            date: activityDate,
            metadata: {},
            sources: {
                tcx: {
                    file: fileName,
                    data: {
                        activity_type: null,
                        activity_id: null,
                        laps: [],
                        trackpoints: []
                    }
                }
            }
        };

        // Store activity type and ID
        if (activityElem) {
            activity.sources.tcx.data.activity_type = activityElem.getAttribute('Sport');
            const idElem = activityElem.querySelector('Id');
            if (idElem) {
                activity.sources.tcx.data.activity_id = idElem.textContent;
            }
        }

        // Parse laps
        const laps = xmlDoc.querySelectorAll('Lap');
        laps.forEach(lap => {
            const lapData = {
                start_time: lap.getAttribute('StartTime'),
                total_time_seconds: parseFloat(this.getElementText(lap, 'TotalTimeSeconds')) || 0,
                distance_meters: parseFloat(this.getElementText(lap, 'DistanceMeters')) || 0,
                maximum_speed: parseFloat(this.getElementText(lap, 'MaximumSpeed')) || 0,
                calories: parseInt(this.getElementText(lap, 'Calories')) || 0
            };

            const avgHR = lap.querySelector('AverageHeartRateBpm Value');
            if (avgHR) {
                lapData.average_heart_rate = parseInt(avgHR.textContent);
            }

            const maxHR = lap.querySelector('MaximumHeartRateBpm Value');
            if (maxHR) {
                lapData.maximum_heart_rate = parseInt(maxHR.textContent);
            }

            activity.sources.tcx.data.laps.push(lapData);
        });

        // Parse trackpoints (first 100 to keep file size manageable)
        const trackpoints = xmlDoc.querySelectorAll('Trackpoint');
        const maxTrackpoints = 100;
        const step = Math.max(1, Math.floor(trackpoints.length / maxTrackpoints));

        for (let i = 0; i < trackpoints.length; i += step) {
            const tp = trackpoints[i];
            const trackpoint = {
                time: this.getElementText(tp, 'Time')
            };

            const position = tp.querySelector('Position');
            if (position) {
                trackpoint.position = {
                    lat: parseFloat(this.getElementText(position, 'LatitudeDegrees')),
                    lon: parseFloat(this.getElementText(position, 'LongitudeDegrees'))
                };
            }

            const altitude = this.getElementText(tp, 'AltitudeMeters');
            if (altitude) {
                trackpoint.altitude_m = parseFloat(altitude);
            }

            const hr = tp.querySelector('HeartRateBpm Value');
            if (hr) {
                trackpoint.heart_rate = parseInt(hr.textContent);
            }

            const speed = tp.querySelector('Extensions Speed');
            if (speed) {
                trackpoint.speed_ms = parseFloat(speed.textContent);
            }

            activity.sources.tcx.data.trackpoints.push(trackpoint);
        }

        return activity;
    }

    /**
     * Parse FIT file (simplified - just extracts metadata)
     */
    parseFIT(buffer, fileName) {
        // FIT file parsing is complex and requires a proper decoder
        // For now, we'll just create a basic activity structure
        const activity = {
            date: this.extractDateFromFilename(fileName),
            metadata: {},
            sources: {
                fit: {
                    file: fileName,
                    data: {
                        note: 'FIT file uploaded but not fully parsed in browser. Use CLI tool for full FIT parsing.'
                    }
                }
            }
        };

        return activity;
    }

    /**
     * Clean CSV row data
     */
    cleanCSVRow(row) {
        const cleaned = {};

        for (const [key, value] of Object.entries(row)) {
            const cleanKey = key.toLowerCase().replace(/\s+/g, '');

            // Try to convert numeric values
            if (value && !isNaN(value) && value.trim() !== '') {
                cleaned[cleanKey] = parseFloat(value);
            } else {
                cleaned[cleanKey] = value;
            }
        }

        return cleaned;
    }

    /**
     * Extract date from filename
     */
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
                    return `${match[1]}${match[2]}${match[3]}`;
                }
            }
        }

        // If no date found, use current date
        const now = new Date();
        return now.toISOString().split('T')[0].replace(/-/g, '');
    }

    /**
     * Get text content from XML element
     */
    getElementText(parent, tagName) {
        const elem = parent.querySelector(tagName);
        return elem ? elem.textContent : null;
    }

    /**
     * Create chunks from activities
     */
    createChunks(activities, chunkSize) {
        if (chunkSize <= 0 || activities.length <= chunkSize) {
            return [activities];
        }

        const chunks = [];
        for (let i = 0; i < activities.length; i += chunkSize) {
            chunks.push(activities.slice(i, i + chunkSize));
        }
        return chunks;
    }

    /**
     * Calculate statistics for a chunk
     */
    calculateChunkStatistics(activities) {
        let totalDistance = 0;
        let totalTimeSeconds = 0;
        let totalCalories = 0;

        activities.forEach(activity => {
            let foundData = false;

            // Try summary field first (copied from CSV)
            if (activity.summary && activity.summary.getdistance) {
                const summary = activity.summary;
                totalDistance += parseFloat(summary.getdistance) || 0;
                totalCalories += parseInt(summary.calories) || 0;
                if (summary.time) {
                    totalTimeSeconds += this.parseTimeString(summary.time);
                }
                foundData = true;
            }
            // Try CSV data path
            else if (activity.sources?.csv?.data?.summary?.getdistance) {
                const summary = activity.sources.csv.data.summary;
                totalDistance += parseFloat(summary.getdistance) || 0;
                totalCalories += parseInt(summary.calories) || 0;
                if (summary.time) {
                    totalTimeSeconds += this.parseTimeString(summary.time);
                }
                foundData = true;
            }

            // Fall back to TCX data if no CSV data found
            if (!foundData && activity.sources?.tcx?.data?.laps) {
                activity.sources.tcx.data.laps.forEach(lap => {
                    totalDistance += (lap.distance_meters || 0) / 1000; // Convert to km
                    totalTimeSeconds += lap.total_time_seconds || 0;
                    totalCalories += lap.calories || 0;
                });
            }
        });

        return {
            total_distance_km: Math.round(totalDistance * 100) / 100,
            total_time_formatted: this.formatTime(totalTimeSeconds),
            total_calories: totalCalories,
            average_distance_per_run: activities.length > 0
                ? Math.round((totalDistance / activities.length) * 100) / 100
                : 0
        };
    }

    /**
     * Parse time string (HH:MM:SS or MM:SS)
     */
    parseTimeString(timeStr) {
        if (!timeStr) return 0;

        const parts = timeStr.trim().split(':').map(p => parseInt(p) || 0);

        if (parts.length === 3) {
            return parts[0] * 3600 + parts[1] * 60 + parts[2];
        } else if (parts.length === 2) {
            return parts[0] * 60 + parts[1];
        }

        return 0;
    }

    /**
     * Format seconds to HH:MM:SS
     */
    formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);

        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    /**
     * Create training log structure
     */
    createTrainingLog(activities, chunkSize = 5) {
        if (activities.length === 0) {
            return { error: 'No activities to process' };
        }

        // Sort activities by date
        activities.sort((a, b) => a.date.localeCompare(b.date));

        const chunks = this.createChunks(activities, chunkSize);

        if (chunks.length === 1 && chunkSize > 0) {
            // Single file output
            return {
                type: 'single',
                data: {
                    metadata: {
                        athlete_name: 'Training Log',
                        created_at: new Date().toISOString(),
                        total_activities: activities.length,
                        data_source: 'Running Watch',
                        purpose: 'Structured Training Data'
                    },
                    activities: activities,
                    statistics: this.calculateChunkStatistics(activities)
                }
            };
        } else {
            // Chunked output
            const chunksData = [];

            chunks.forEach((chunk, idx) => {
                const chunkLog = {
                    metadata: {
                        athlete_name: 'Training Log',
                        created_at: new Date().toISOString(),
                        chunk_number: idx + 1,
                        total_chunks: chunks.length,
                        total_activities: chunk.length,
                        data_source: 'Running Watch',
                        purpose: 'Structured Training Data (Chunk)',
                        statistics: this.calculateChunkStatistics(chunk)
                    },
                    activities: chunk
                };

                chunksData.push({
                    fileName: `training_log_part${idx + 1}.json`,
                    data: chunkLog,
                    info: {
                        file: `training_log_part${idx + 1}.json`,
                        chunk_number: idx + 1,
                        activity_count: chunk.length,
                        date_range: {
                            first_activity: chunk[0]?.date || null,
                            last_activity: chunk[chunk.length - 1]?.date || null
                        },
                        statistics: this.calculateChunkStatistics(chunk)
                    }
                });
            });

            // Create index file
            const indexData = {
                metadata: {
                    created_at: new Date().toISOString(),
                    total_chunks: chunks.length,
                    total_activities: activities.length,
                    purpose: 'Index file for chunked training log'
                },
                chunks: chunksData.map(c => c.info)
            };

            return {
                type: 'chunked',
                chunks: chunksData,
                index: {
                    fileName: 'training_log_index.json',
                    data: indexData
                },
                statistics: this.calculateChunkStatistics(activities)
            };
        }
    }
}

// Export for use in app.js
window.RunLogParser = RunLogParser;
