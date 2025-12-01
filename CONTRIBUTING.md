# Contributing to E-commerce ETL Project

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ecommerce-etl-project.git
   cd ecommerce-etl-project
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow PEP 8 style guidelines
   - Add docstrings to functions and classes
   - Include type hints where applicable
   - Write meaningful commit messages

3. **Test your changes**:
   ```bash
   pytest tests/
   python run_all.py  # Run full pipeline
   ```

4. **Commit your work**:
   ```bash
   git commit -am "Brief description of changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub with a clear description of changes

## Pull Request Guidelines

- Provide a clear description of the problem and solution
- Link related issues using `closes #issue_number`
- Include before/after examples if applicable
- Ensure all tests pass and code is properly formatted
- Add docstrings and type hints for new functions

## Code Style

We follow PEP 8 with these guidelines:

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings using Google-style format:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """Brief description.
      
      Longer description if needed.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
          
      Raises:
          ValueError: When something goes wrong
      """
  ```

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
[type]: Brief description

Longer explanation of changes if needed.

Closes #issue_number
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Test additions/changes

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Relevant log files or error messages

## Questions?

Feel free to open an issue for questions or discussions. We're here to help!

Thank you for contributing! 🙏
