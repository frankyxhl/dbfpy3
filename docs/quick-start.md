# Quick Start - dbfpy3 Development

**Get up to speed in < 2 minutes**

## Current Focus
Working on FoxPro field type support. Just completed Double field type B implementation.

## Latest Changes (2025-08-31)
```python
# NEW: FoxPro Double field support (type B)
from dbfpy3 import dbf

db = dbf.Dbf('data.dbf', new=True)
db.add_field(
    ('B', 'LATITUDE', 8),   # NEW: Double precision field
    ('B', 'LONGITUDE', 8),  # 15-17 decimal digits precision
)
rec = db.new()
rec['LATITUDE'] = 40.748817123456789  # High precision preserved
rec['LONGITUDE'] = -73.985428987654321
db.write(rec)
db.close()
```

## Project State
- **Branch**: develop (1 commit ahead)
- **Tests**: 197/197 passing (100%)
- **Uncommitted**: Double field implementation ready to commit
- **Next**: Commit, version bump to 4.3.0, potential release

## Key Files Modified
```bash
dbfpy3/fields.py         # Added DbfDoubleField class
tests/test_double_field.py  # 9 new test cases
README.md               # Documentation and examples
```

## To Continue Work
```bash
# Check current state
git status
python -m unittest discover tests  # Verify all tests pass

# Commit the Double field feature
git add dbfpy3/fields.py tests/test_double_field.py README.md
git commit -m "feat: Add FoxPro Double field type B support"

# Consider release
# Update version in setup.py to 4.3.0
# Update HISTORY.rst with changelog
# Push and create PR/release
```

## Architecture Quick Reference

### Field Types Now Supported
- **B** - Double (NEW) - IEEE 754 double-precision
- C - Character
- N - Numeric  
- D - Date
- L - Logical
- M - Memo
- F - Float
- I - Integer
- Y - Currency
- T - DateTime
- G - General

### Core Classes
- `Dbf` - Main database class
- `DbfHeader` - File header management
- `DbfRecord` - Individual records
- `DbfField` - Base field class
- `DbfDoubleField` - New Double field implementation

### Testing
```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_double_field

# Run with coverage
coverage run -m unittest discover
coverage report
```

## Common Operations

### Read DBF file
```python
with dbf.Dbf('file.dbf') as db:
    for record in db:
        print(record['FIELD_NAME'])
```

### Create new DBF
```python
db = dbf.Dbf('new.dbf', new=True)
db.add_field(('C', 'NAME', 30))
rec = db.new()
rec['NAME'] = 'Value'
db.write(rec)
db.close()
```

## Need More Context?
- See `/docs/sessions/` for detailed session records
- Check `/docs/project-status.md` for current priorities
- Review `/docs/decision-log.md` for architecture choices