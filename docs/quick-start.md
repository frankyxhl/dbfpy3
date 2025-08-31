# Quick Start - dbfpy3 Development

**Get up to speed in < 2 minutes**

## Current Focus
**CRITICAL**: Just fixed data integrity bug - header record count wasn't persisting. Must commit ASAP.
Also completed FoxPro Double field type B implementation.

## Latest Changes (2025-08-31)

### CRITICAL BUG FIX
```python
# FIXED: Header record count now properly persists
# Bug: New records were lost when file was reopened
# Fix: Set header._changed = True when incrementing record_count
# File: dbfpy3/dbf.py line 208
```

### NEW FEATURE
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
- **Branch**: develop (2 commits ahead)
- **Tests**: 200/200 passing (100%, 26 skipped)
- **Uncommitted**: 
  - **CRITICAL**: Header record count fix in dbf.py
  - Test file: test_header_record_count.py
  - Double field implementation from earlier
- **Next**: URGENT - Commit critical fix, then version bump for patch release

## Key Files Modified
```bash
# CRITICAL FIX (uncommitted)
dbfpy3/dbf.py                    # Fixed header._changed flag bug
tests/test_header_record_count.py  # 3 test cases for regression prevention

# Feature addition (committed)
dbfpy3/fields.py                # Added DbfDoubleField class
tests/test_double_field.py      # 9 new test cases
README.md                       # Documentation and examples
```

## To Continue Work
```bash
# URGENT - Commit critical bug fix first!
git add dbfpy3/dbf.py tests/test_header_record_count.py
git commit -m "fix: Critical - Set header._changed flag when updating record count

Fixes data loss bug where new records weren't persisted to disk.
The header record count was incremented but _changed flag wasn't set,
causing flush() to skip writing the updated header."

# Then verify everything works
python3 -m unittest discover tests  # Should show 200 tests passing

# Consider immediate patch release (4.3.1)
# This is a critical data integrity fix!
# Update version in setup.py
# Update HISTORY.rst with CRITICAL FIX notice
# Push and create urgent PR/release
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