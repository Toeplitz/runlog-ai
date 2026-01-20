# Contributing to runlog-ai

Thank you for your interest in contributing to runlog-ai! This document provides guidelines for contributing to the project.

## Ways to Contribute

### Report Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Sample data files (if possible and privacy-safe)

### Suggest Features

Have an idea for a new feature? Open an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation ideas you have

### Improve Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve existing guides
- Translate documentation

### Submit Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m "Add feature: description"`
6. **Push to your fork**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Code Guidelines

### Python Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### Example:

```python
def parse_activity(self, date_folder: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Parse all data files for a single activity.

    Args:
        date_folder: Path to the activity folder (YYYYMMDD format)
        verbose: Whether to print progress messages

    Returns:
        Dictionary containing parsed activity data with metadata and sources
    """
    # Implementation here
```

### Testing

- Test your changes with real Coros data files
- Ensure backwards compatibility
- Test on multiple Python versions if possible (3.6+)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/runlog-ai.git
cd runlog-ai

# Install dependencies
pip install -r requirements.txt

# Make your changes
# ...

# Test with sample data
python3 parse_coros_data.py --single-date YYYYMMDD
```

## Project Structure

```
runlog-ai/
├── parse_coros_data.py       # Main parser script
├── view_training_data.py     # Data viewer
├── create_training_log.py    # Training log aggregator
├── metadata_template.json    # Template for activity metadata
├── README.md                 # Main documentation
├── QUICK_START.md           # Quick start guide
├── METADATA_GUIDE.md        # Metadata documentation
├── README_PARSER.md         # Parser technical details
├── requirements.txt         # Python dependencies
└── LICENSE                  # MIT License
```

## Feature Ideas

Looking for ideas? Here are some features we'd love to see:

### High Priority
- [ ] Support for Garmin data exports
- [ ] Support for Polar data exports
- [ ] Visualization of GPS routes
- [ ] Heart rate zone analysis
- [ ] Training load calculations

### Medium Priority
- [ ] Export to other formats (GPX, CSV)
- [ ] Web interface for viewing data
- [ ] Automatic activity detection and organization
- [ ] Statistical analysis and trends
- [ ] Compare multiple activities

### Low Priority
- [ ] Mobile app support
- [ ] Cloud sync options
- [ ] Social features (share workouts)
- [ ] Integration with Strava, TrainingPeaks

## Adding Support for New Watch Brands

If you want to add support for other running watches:

1. Check the export format (FIT, TCX, CSV, or proprietary)
2. If it's FIT/TCX, it likely already works!
3. If proprietary, create a new parser module
4. Add tests with sample data
5. Update documentation

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Provide context for what you're trying to do

## Code of Conduct

Be respectful and constructive:
- Be welcoming to newcomers
- Respect different viewpoints
- Focus on what's best for the project
- Show empathy towards other community members

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make runlog-ai better!**
