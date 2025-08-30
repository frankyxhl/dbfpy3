# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

dbfpy3 is a Pure Python 3 library for reading and writing DBF (dBase/FoxPro) database files. It's a clean, focused implementation with no external dependencies, supporting FoxPro DBF files, memo fields (.FPT), and code page encoding.

## Essential Commands

### Development
```bash
# Run tests
python -m unittest discover tests
make test

# Run specific test module  
python -m unittest tests.test_fields

# Check code style
make lint
flake8 dbfpy3 tests

# Generate coverage report
make coverage

# Clean build artifacts
make clean
```

### Building and Distribution
```bash
# Build distribution packages
make dist
python setup.py sdist bdist_wheel

# Install locally for development
pip install -e .

# Release workflow (maintainers only)
make release
```

### Documentation
```bash
# Build documentation
cd docs && make html

# Clean documentation
cd docs && make clean
```

## Architecture

### Core Module Structure (`dbfpy3/`)

The library follows a simple, focused architecture:

1. **`dbf.py`** - Main `Dbf` class providing the primary API
2. **`header.py`** - `DbfHeader` class for DBF file headers and metadata  
3. **`fields.py`** - Field type system and validation
4. **`record.py`** - `DbfRecord` class for individual database records
5. **`memo.py`** - FoxPro memo field (.FPT) support
6. **`code_page.py`** - Character encoding support
7. **`utils.py`** - Shared utilities and helpers

### Key Design Principles

- **Simplicity** - Clean, readable code with minimal complexity
- **No Dependencies** - Pure Python implementation 
- **Context Manager Support** - Safe resource management
- **FoxPro Compatibility** - Full support for FoxPro DBF format
- **Character Encoding** - Proper international character support

## Common Usage Patterns

```python
from dbfpy3 import dbf

# Reading with context manager (recommended)
with dbf.Dbf('data.dbf') as db:
    for record in db:
        print(record['NAME'])

# Creating new files
db = dbf.Dbf('new.dbf', new=True)
db.add_field(('C', 'NAME', 15), ('D', 'BIRTHDATE'))
rec = db.new()
rec['NAME'] = 'John'
db.write(rec)
db.close()
```

## Testing Approach

Tests use Python's built-in `unittest` framework:
- `tests/test_dbfpy3.py` - Main integration tests
- `tests/test_fields.py` - Field type validation
- `tests/test_code_page.py` - Character encoding tests
- `tests/test_memo.py` - Memo field handling tests

Run individual test files:
```bash
python -m unittest tests.test_fields
```

## Code Style

- Follow PEP 8 style guidelines
- Use clear, descriptive variable names
- Keep functions focused and single-purpose
- Include docstrings for public APIs
- Maintain backward compatibility

## Important Notes

- The library includes warnings about being "not fully tested" - this is historical
- Field names are limited to 10 characters per DBF specification
- DBF files use code pages for character encoding, not UTF-8
- Context managers (`with` statements) are recommended for resource safety

## File Organization

```
dbfpy3/
├── dbfpy3/           # Core library modules
├── tests/            # Unit test suite
├── docs/             # Sphinx documentation
├── examples/         # Usage examples
├── README.md         # Project overview
├── CONTRIBUTING.rst  # Contributor guidelines
├── HISTORY.rst       # Changelog
└── setup.py          # Package configuration
```

## Development Workflow

1. **Make changes** to core modules in `dbfpy3/`
2. **Add/update tests** in `tests/` 
3. **Run test suite** with `make test`
4. **Update documentation** if APIs change
5. **Check code style** with `make lint`
6. **Build and test locally** before submitting changes

This library prioritizes simplicity, reliability, and compatibility over advanced features.