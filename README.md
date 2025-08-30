# dbfpy3

[![Python Version](https://img.shields.io/pypi/pyversions/dbfpy3.svg)](https://pypi.org/project/dbfpy3/)
[![PyPI Version](https://img.shields.io/pypi/v/dbfpy3.svg)](https://pypi.org/project/dbfpy3/)
[![License](https://img.shields.io/pypi/l/dbfpy3.svg)](https://pypi.org/project/dbfpy3/)
[![Tests](https://github.com/frankyxhl/dbfpy3/workflows/Tests/badge.svg)](https://github.com/frankyxhl/dbfpy3/actions)

Pure Python 3 library for reading and writing DBF (dBase/FoxPro) database files. No external dependencies required.

## ✨ Features

- **Pure Python** - No C extensions or external dependencies
- **FoxPro Support** - Full support for FoxPro DBF files and memo fields (.FPT)
- **Code Page Support** - Proper character encoding for international data
- **Context Manager** - Safe resource management with `with` statements
- **Python 3.5+** - Modern Python support

## 🚀 Quick Start

### Installation

```bash
pip install dbfpy3
```

### Basic Usage

```python
from dbfpy3 import dbf

# Read existing DBF file
with dbf.Dbf('customers.dbf') as db:
    for record in db:
        print(record['NAME'], record['EMAIL'])

# Create new DBF file
db = dbf.Dbf('new_file.dbf', new=True)
db.add_field(
    ('C', 'NAME', 30),      # Character field, max 30 chars
    ('D', 'BIRTHDATE'),     # Date field
    ('N', 'SALARY', 10, 2), # Numeric field, 10 digits, 2 decimal places
    ('L', 'ACTIVE')         # Logical field (True/False)
)

# Add records
rec = db.new()
rec['NAME'] = 'John Doe'
rec['BIRTHDATE'] = datetime.date(1990, 1, 15)
rec['SALARY'] = 75000.50
rec['ACTIVE'] = True
db.write(rec)
db.close()
```

## 📖 Documentation

- [Quick Start Guide](docs/usage.rst) - Get up and running quickly
- [API Documentation](docs/index.rst) - Complete API reference
- [Examples](examples/) - Sample code and use cases
- [Contributing](CONTRIBUTING.rst) - How to contribute

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/frankyxhl/dbfpy3.git
cd dbfpy3

# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
python -m unittest discover tests
make test

# Run specific test module
python -m unittest tests.test_fields

# Check code style
make lint
```

## ⚠️ Important Notes

- **Field Names**: Limited to 10 characters per DBF specification
- **Unicode Support**: DBF files use code pages for character encoding
- **Production Use**: While functional, use with caution in production environments

## 📄 License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Original Author**: Jeff Kunce
- **Python 3 Port**: Frank Xu
- **Contributors**: Hans Fiby, Zdeněk Böhm, and many others

## 🔗 Links

- [PyPI Package](https://pypi.org/project/dbfpy3/)
- [GitHub Repository](https://github.com/frankyxhl/dbfpy3)
- [Documentation](docs/index.rst)
- [Changelog](HISTORY.rst)