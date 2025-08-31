# Quick Start Guide - dbfpy3

## 2-Minute Context

**What**: Pure Python 3 library for reading/writing DBF (dBase/FoxPro) files
**Status**: Production ready - all tests passing (0 failures, 26 design skips)
**Branch**: develop (clean, no uncommitted changes)
**Last Work**: Fixed comprehensive test suite - reduced failures from 147 to 0

## Recent Session Summary (2025-08-31)

Fixed all critical bugs and test failures:
1. ✅ dBase III compatibility (field alignment tolerance)
2. ✅ Standardized field definition order (type, name, length)
3. ✅ Added missing `__contains__` to DbfRecord
4. ✅ Fixed numeric field None handling
5. ✅ Fixed header tuple initialization
6. ✅ Cleaned up repository (__pycache__, .gitignore)

## Key Files & Locations

### Core Library
```
/Users/frank/Projects/dbfpy3/dbfpy3/
├── dbf.py        # Main Dbf class (primary API)
├── header.py     # DbfHeader (includes dBase III tolerance fix)
├── fields.py     # Field type system (None handling fixes)
├── record.py     # DbfRecord (magic methods added)
├── memo.py       # FoxPro memo support
└── utils.py      # Utilities
```

### Tests
```
/Users/frank/Projects/dbfpy3/tests/
├── test_*_tdd.py         # TDD unit tests (comprehensive)
├── test_*_bdd.py         # BDD behavior tests
└── test_dbfpy3.py        # Original integration tests
```

## Quick Commands

```bash
# Navigate to project
cd /Users/frank/Projects/dbfpy3

# Run all tests (should show 0 failures, 26 skipped)
python3 -m unittest discover tests

# Run specific test file
python3 -m unittest tests.test_field_parsing_tdd

# Check git status (should be clean)
git status

# View recent changes
git log --oneline -5

# See what was fixed
git diff 56ec087..HEAD
```

## Current Test Status
- **Total**: 188 tests
- **Passing**: 162 ✅
- **Failing**: 0 ✅
- **Skipped**: 26 (intentional - advanced features not in scope)

## Design Decisions

### What's Supported
- dBase III files (0x03, 0x83 signatures)
- FoxPro DBF files
- Memo fields (.FPT)
- Character encodings (code pages)
- Context managers
- Negative indexing
- Field containment checks

### What's Not Supported (By Design)
- AutoIncrement fields
- Binary/Timestamp fields
- Transactions
- Multi-threading
- External indexes
- Custom validators

## Next Steps If Continuing

1. **If adding features**: Check skipped tests for implementation templates
2. **If fixing bugs**: Run test suite first to ensure no regressions
3. **If documenting**: Update README.md with feature matrix
4. **If releasing**: Version is 4.2.3, all tests passing

## Problem Resolution Patterns

### If Tests Fail
1. Check field definition order (should be: type, name, length)
2. Verify dBase III tolerance in header.py
3. Ensure proper None handling in numeric fields
4. Check for missing magic methods in DbfRecord

### Common Issues Fixed
- "fields start does not match" → dBase III tolerance added
- "'field' in record" fails → __contains__ method added
- "None in numeric field" → Converts to empty string
- "record[-1]" fails → Negative indexing fixed

## Repository State
- Branch: `develop` (clean)
- Latest commit: `64bd301` - Cleanup __pycache__ directories
- Previous commit: `56ec087` - Added TDD/BDD test suites
- Python version: 3.13 (works with 3.6+)
- Dependencies: None (pure Python)