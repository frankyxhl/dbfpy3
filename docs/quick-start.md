# Quick Start - dbfpy3 Development

**Get up to speed in < 2 minutes**

## Current Focus
**v5.0.0 Ready**: Complete pandas integration with DataFrame support
**v4.2.4 Released**: Critical data integrity bug fixed

## Latest Changes (2025-08-31)

### MAJOR FEATURE: Pandas Integration (v5.0.0)
```python
# NEW: Complete DataFrame support
from dbfpy3.pandas_integration import read_dbf, write_dbf
import pandas as pd

# Read DBF to DataFrame
df = read_dbf('legacy_data.dbf', encoding='cp1252')

# Analyze with pandas
stats = df.describe()
pivot = df.pivot_table(values='SALES', index='REGION')

# Write DataFrame to DBF
write_dbf(df, 'output.dbf', encoding='cp1252')

# Advanced: Custom field specifications
write_dbf(df, 'optimized.dbf', field_specs={
    'price': ('N', 10, 2),  # Numeric with 2 decimals
    'notes': ('M', 0, 0),    # Memo field
})
```

### CRITICAL BUG FIX (v4.2.4)
```python
# FIXED: Header record count now properly persists
# Bug: New records were lost when file was reopened
# Fix: Set header._changed = True when incrementing record_count
# File: dbfpy3/dbf.py line 208
```

## Project State
- **Branch**: develop (3 commits ahead)
- **Tests**: 217/217 passing (100% - includes new pandas tests)
- **Uncommitted**: 
  - Pandas integration module and tests
  - Documentation updates
  - Makefile and .gitignore improvements
- **Next**: Commit pandas work, prepare v5.0.0 release

## Key Files Modified
```bash
# Pandas Integration (uncommitted)
dbfpy3/pandas_integration.py           # Complete DataFrame support
tests/test_pandas_integration_tdd.py   # 17 comprehensive tests
features/pandas_*.feature              # 4 BDD scenarios
docs/pandas_integration_guide.md       # Full documentation
ROADMAP_5.0.md                         # Release planning

# Critical Fix (committed)
dbfpy3/dbf.py                          # Fixed header._changed flag bug

# Double Field (committed)  
dbfpy3/fields.py                       # Added DbfDoubleField class
```

## To Continue Work
```bash
# 1. Commit pandas integration
git add dbfpy3/pandas_integration.py tests/test_pandas_integration_tdd.py
git add features/pandas*.feature docs/pandas_integration_guide.md
git add ROADMAP_5.0.md .gitignore Makefile
git commit -m "feat: Add complete pandas DataFrame integration (v5.0.0)

Major feature addition with bidirectional DataFrame conversion,
intelligent type mapping, and chunked processing for large files."

# 2. Verify all tests pass
python3 -m unittest discover tests  # Should show 217 tests passing
behave features/                    # Run BDD scenarios

# 3. Prepare v5.0.0 release
# - Update version in setup.py to 5.0.0
# - Add pandas as optional dependency in setup.py extras_require
# - Update README with pandas examples
# - Tag and release

# 4. Consider v4.2.4 hotfix branch
# Cherry-pick critical fix to main for immediate release
```

## Architecture Quick Reference

### Pandas Type Mapping
```python
# Pandas → DBF
int64      → 'N' (Numeric, 18 digits)
float64    → 'B' (Double, IEEE 754)
object/str → 'C' (Character, auto-sized)
datetime64 → 'D' (Date)
bool       → 'L' (Logical)

# DBF → Pandas
'C' → object (string)
'N' → int64/float64 (based on decimals)
'D' → datetime64[ns]
'L' → bool
'B' → float64
'M' → object (memo text)
```

### Field Types Supported
- **B** - Double - IEEE 754 double-precision
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
- `DbfDoubleField` - Double field implementation
- `DbfPandasConverter` - NEW: DataFrame converter

### Pandas API
- `read_dbf()` - Read DBF to DataFrame
- `write_dbf()` - Write DataFrame to DBF
- `DbfPandasConverter` - Class-based conversion

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

### Read DBF file (Traditional)
```python
with dbf.Dbf('file.dbf') as db:
    for record in db:
        print(record['FIELD_NAME'])
```

### Read DBF to DataFrame (NEW)
```python
from dbfpy3.pandas_integration import read_dbf
df = read_dbf('file.dbf', encoding='cp1252')
print(df.head())
```

### Create DBF from DataFrame (NEW)
```python
from dbfpy3.pandas_integration import write_dbf
import pandas as pd

df = pd.DataFrame({
    'NAME': ['Alice', 'Bob'],
    'AGE': [30, 25],
    'JOINED': pd.to_datetime(['2020-01-01', '2021-06-15'])
})
write_dbf(df, 'output.dbf')
```

## Need More Context?
- See `/docs/sessions/` for detailed session records
- Check `/docs/project-status.md` for current priorities
- Review `/docs/decision-log.md` for architecture choices