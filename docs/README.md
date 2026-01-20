# RunLog AI Web App

This is the client-side web application for RunLog AI. It runs entirely in your browser - no data is sent to any server.

## Features

- **Privacy First**: All file processing happens in your browser
- **Multi-File Upload**: Upload FIT, TCX, and CSV files
- **Automatic Grouping**: Files are automatically grouped by date
- **Smart Chunking**: Creates manageable 5-10MB chunks perfect for AI tools
- **Instant Downloads**: Download processed JSON files immediately

## How to Use

1. **Upload Files**: Drag and drop or browse for your running watch files
2. **Configure Options**: Set chunk size and GPS options
3. **Process**: Click "Process Files" to parse your data
4. **Download**: Download the generated JSON files

## File Organization

The app automatically groups files by date (extracted from filenames). For example:

```
20251202_activity.fit
20251202_activity.tcx
20251202_activity.csv
```

Will be grouped together and combined into a single activity for that date.

## Supported Formats

- **FIT** (.fit) - Garmin, Coros, and other watches
- **TCX** (.tcx) - Training Center XML format
- **CSV** (.csv) - Coros CSV exports

## Local Development

To run locally:

```bash
# Serve the docs folder with any static server
python3 -m http.server 8000 --directory docs

# Or use Node's http-server
npx http-server docs

# Open http://localhost:8000
```

## GitHub Pages

This app is automatically deployed to GitHub Pages when pushed to the `main` branch.

Access it at: `https://<username>.github.io/runlog-ai`
