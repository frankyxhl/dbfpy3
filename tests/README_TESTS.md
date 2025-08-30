# dbfpy3 Test Suite Documentation

This document describes the comprehensive Test-Driven Development (TDD) and Behavior-Driven Development (BDD) test suite for the dbfpy3 library.

## Overview

The test suite follows both TDD and BDD methodologies to ensure comprehensive coverage of:
- Individual component functionality (TDD)
- User behavior scenarios (BDD)
- Edge cases and error conditions
- dBase III format compatibility
- Data integrity and validation

## Test Structure

### Existing Tests (Original)
- `test_dbfpy3.py` - Basic integration tests
- `test_fields.py` - Field type validation tests
- `test_code_page.py` - Character encoding tests
- `test_memo.py` - Memo field handling tests
- `test_dbase3.py` - dBase III format support tests

### New TDD Tests (Comprehensive Unit Tests)
- `test_field_parsing_tdd.py` - Field parsing with edge cases and boundary conditions
- `test_header_validation_tdd.py` - Header structure validation and error handling
- `test_record_operations_tdd.py` - Record reading/writing operations and data integrity
- `test_error_handling_tdd.py` - Error handling, file operations, and boundary conditions

### New BDD Tests (Behavior Scenarios)
- `test_dbf_behavior_bdd.py` - User story scenarios with Given-When-Then structure

### New dBase III Comprehensive Tests
- `test_dbase3_comprehensive_tdd.py` - Comprehensive dBase III format support

## Running Tests

### Run All Tests
```bash
python3 -m unittest discover tests -v
```

### Run Specific Test Categories

#### Original Tests Only
```bash
python3 -m unittest tests.test_fields tests.test_code_page tests.test_memo tests.test_dbase3 -v
```

#### TDD Tests Only
```bash
python3 -m unittest tests.test_field_parsing_tdd tests.test_header_validation_tdd tests.test_record_operations_tdd tests.test_error_handling_tdd -v
```

#### BDD Tests Only
```bash
python3 -m unittest tests.test_dbf_behavior_bdd -v
```

#### dBase III Tests Only
```bash
python3 -m unittest tests.test_dbase3 tests.test_dbase3_comprehensive_tdd -v
```

#### Run Individual Test Files
```bash
python3 -m unittest tests.test_field_parsing_tdd -v
```

## Test Methodology

### TDD (Test-Driven Development)
The TDD tests follow the Red-Green-Refactor cycle:

1. **Red Phase**: Write failing tests that describe the desired functionality
2. **Green Phase**: Write minimal code to make tests pass
3. **Refactor Phase**: Improve code while keeping tests green

#### TDD Test Structure Example:
```python
def test_field_parsing_with_exact_32_bytes_should_succeed(self):
    """
    GIVEN: A field definition with exactly 32 bytes
    WHEN: Parsing the field bytes
    THEN: Should create a valid DbfCharacterField
    """
    field = DbfFields.parse(self.valid_field_bytes)
    
    self.assertIsInstance(field, DbfCharacterField)
    self.assertEqual(field.name, b'NAME')
    self.assertEqual(field.length, 10)
```

### BDD (Behavior-Driven Development)
The BDD tests use Given-When-Then structure to describe user scenarios:

#### BDD Test Structure Example:
```python
def test_user_creates_new_empty_dbf_file(self):
    """
    User Story: As a developer, I want to create a new empty DBF file
    so that I can start building a database structure.

    Scenario: Creating a new empty DBF file
    """
    # GIVEN: I need to create a new DBF file
    file_path = self.temp_path
    self.assertFalse(os.path.exists(file_path))

    # WHEN: I create a new DBF file with basic structure
    db = dbf.Dbf(file_path, new=True)
    db.add_field(("ID", "N", 5, 0))
    db.close()

    # THEN: The file should be created with proper DBF structure
    self.assertTrue(os.path.exists(file_path))
```

## Test Categories and Coverage

### 1. Field Parsing Tests (`test_field_parsing_tdd.py`)
- **Purpose**: Test field definition parsing with edge cases
- **Coverage**:
  - Field parsing with various byte lengths
  - Field type registration and retrieval
  - Field encoding/decoding operations
  - Boundary conditions (0 bytes, 33 bytes, etc.)
  - All supported field types (C, N, F, D, L, M, Y, I, T, P, G)
  - Error handling for invalid field definitions

### 2. Header Validation Tests (`test_header_validation_tdd.py`)
- **Purpose**: Test DBF header structure and validation
- **Coverage**:
  - Header initialization with various parameters
  - Signature validation (dBase III, FoxPro variants)
  - Field management operations
  - Header serialization/deserialization
  - Code page support
  - Validation and error conditions

### 3. Record Operations Tests (`test_record_operations_tdd.py`)
- **Purpose**: Test record creation, reading, and writing
- **Coverage**:
  - Record creation and initialization
  - Field access by name and index
  - Record serialization/deserialization
  - Data validation and type conversion
  - Integration with DBF files
  - Multi-record operations

### 4. Error Handling Tests (`test_error_handling_tdd.py`)
- **Purpose**: Test error conditions and boundary cases
- **Coverage**:
  - File operation errors (missing files, permissions, corruption)
  - Field boundary conditions (max length, overflow)
  - Record boundary conditions (unicode, null values)
  - Memory and performance limits
  - Data integrity validation

### 5. BDD Behavior Tests (`test_dbf_behavior_bdd.py`)
- **Purpose**: Test user scenarios and workflows
- **Coverage**:
  - DBF file creation workflows
  - File reading and data access patterns
  - Error recovery scenarios
  - Data integrity scenarios
  - Version compatibility behaviors

### 6. Comprehensive dBase III Tests (`test_dbase3_comprehensive_tdd.py`)
- **Purpose**: Comprehensive dBase III format support
- **Coverage**:
  - Header structure compliance
  - Field definition parsing
  - Record handling and encoding
  - Memo field support (.FPT files)
  - Compatibility with legacy files
  - Field alignment handling

## Test Data and Fixtures

### Common Test Patterns
- Use `tempfile.NamedTemporaryFile()` for temporary DBF files
- Clean up test files in `tearDown()` methods
- Use `unittest.mock` for dependency isolation
- Parameterized tests with `subTest()` for multiple scenarios

### Test Data Examples
```python
# Field definition test data
valid_field_bytes = struct.pack(
    '< 11s c L 2B 14s',
    b'NAME',           # Field name
    b'C',              # Field type
    0,                 # Displacement
    10,                # Length
    0,                 # Decimal count
    b'\x00' * 14,      # Reserved
)

# Sample employee data for integration tests
sample_employees = [
    (1, "John Doe", "Engineering", 75000.00, True),
    (2, "Jane Smith", "Marketing", 68000.50, True),
    (3, "Bob Johnson", "Sales", 62000.25, False),
]
```

## Known Test Results

### Passing Tests
- All original tests (15 tests) pass successfully
- Tests demonstrate the current functionality works correctly
- dBase III signature support is properly implemented
- Field parsing and basic operations are functional

### Failing/Error Tests
- Some new comprehensive tests may fail, which is expected
- These failures indicate areas for improvement in the implementation
- Tests serve as specifications for future development
- Error tests help identify edge cases that need handling

### Test Output Interpretation
- **OK**: Test passes - functionality works as expected
- **FAIL**: Test fails - assertion not met, needs implementation fix
- **ERROR**: Test error - exception during test execution, needs investigation
- **ResourceWarning**: File handle not properly closed (cleanup issue)

## Contributing New Tests

### TDD Test Guidelines
1. Start with a failing test that describes desired behavior
2. Use descriptive test names: `test_should_[expected]_when_[condition]`
3. Follow Arrange-Act-Assert pattern
4. Include comprehensive docstring with Given-When-Then structure
5. Test one behavior per test method
6. Use `subTest()` for parameterized testing

### BDD Test Guidelines
1. Start with user stories: "As a [user], I want [goal] so that [reason]"
2. Use scenario descriptions: "Scenario: [specific behavior]"
3. Structure with Given-When-Then comments
4. Focus on business value and user outcomes
5. Include realistic test data and workflows

### Test Organization
- Group related tests in the same test class
- Use descriptive class names: `TestFieldParsingTDD`
- Include comprehensive docstrings at module and class level
- Follow consistent naming conventions
- Ensure proper setup and teardown of test fixtures

## Test Coverage Goals

- **Line Coverage**: Aim for 85%+ line coverage
- **Branch Coverage**: Test all conditional paths
- **Edge Cases**: Cover boundary conditions and error states
- **Integration**: Test component interactions
- **Regression**: Prevent breaking changes

## Continuous Testing

### Development Workflow
1. Write failing test (Red)
2. Implement minimal code to pass (Green)
3. Refactor while keeping tests green (Refactor)
4. Run full test suite before commits
5. Add regression tests for bug fixes

### Automation
- Tests can be integrated into CI/CD pipelines
- Use `make test` for convenient test running
- Monitor test performance and execution time
- Track test coverage over time

## Troubleshooting Tests

### Common Issues
- **File permission errors**: Ensure temp directories are writable
- **Resource warnings**: Add proper file cleanup in tearDown
- **Import errors**: Check Python path and module structure
- **Encoding issues**: Handle different character encodings in tests

### Debug Tips
- Use `python3 -m unittest tests.specific_test -v` for detailed output
- Add print statements or use debugger for investigation
- Check temp file contents when tests fail
- Verify test data matches expected format

This test suite provides comprehensive coverage of the dbfpy3 library functionality and serves as both validation and documentation of the expected behavior.