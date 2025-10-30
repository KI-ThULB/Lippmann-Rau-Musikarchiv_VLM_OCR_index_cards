# Contributing to Lippmann-Rau Archive OCR

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, model used)
- Relevant log excerpts from `vlm_errors.log`

### Suggesting Enhancements

We welcome feature requests! Please create an issue with:
- Clear description of the enhancement
- Use case / motivation
- Possible implementation approach (optional)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/lippmann-rau-ocr.git
   cd lippmann-rau-ocr
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Test with a small batch first
   python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Clear description of your changes"
   ```
   
   Commit message format:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements
   - `Docs:` for documentation

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style Guidelines

### Python

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and short
- Use type hints where appropriate

Example:
```python
def process_card(image_path: str, api_key: str) -> dict:
    """
    Process a single index card.
    
    Args:
        image_path: Path to the image file
        api_key: API authentication key
        
    Returns:
        Dictionary with extracted metadata
    """
    # Implementation
    pass
```

### Comments

- Use comments to explain **why**, not **what**
- Document complex algorithms
- Keep comments up-to-date with code changes

### Error Handling

- Always use try-except blocks for I/O operations
- Log errors with sufficient context
- Don't silently ignore exceptions

## 🧪 Testing

Before submitting a PR:

1. Test with a small batch (1-2 folders)
2. Verify CSV output format
3. Check error handling with invalid images
4. Ensure checkpoints work correctly

## 📚 Documentation

When adding features:

- Update README.md if user-facing
- Update inline code comments
- Add examples if applicable
- Update CHANGES.md

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Web interface for quality control
- [ ] Support for additional VLM models
- [ ] Batch processing statistics dashboard
- [ ] Export to MARC/Dublin Core formats

### Medium Priority
- [ ] Unit tests
- [ ] Configuration file support (YAML/JSON)
- [ ] Multi-language support for UI
- [ ] Docker containerization

### Enhancement Ideas
- [ ] Image preprocessing pipeline
- [ ] OCR confidence scoring
- [ ] Duplicate detection
- [ ] Integration with archive management systems

## 🔍 Code Review Process

1. Maintainer reviews your PR
2. Feedback provided (if needed)
3. You address feedback
4. PR merged once approved

## 💬 Communication

- **Issues**: For bugs and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For questions and ideas

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Other unprofessional conduct

## 🙏 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Acknowledged in academic citations (if applicable)

## ❓ Questions?

Feel free to:
- Open an issue for questions
- Contact the maintainer directly
- Check existing issues and PRs

---

Thank you for helping improve this project! 🎵📚
