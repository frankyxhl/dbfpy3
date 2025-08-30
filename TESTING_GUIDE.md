# Testing Guide for dbfpy3

This guide explains how to run the comprehensive test suite for dbfpy3, which includes both TDD (Test-Driven Development) and BDD (Behavior-Driven Development) tests.

## Quick Start

```bash
# Run all TDD tests
make tdd

# Run all BDD tests
make bdd

# Run both TDD and BDD tests
make tdd && make bdd
```

## TDD (Test-Driven Development) Tests

TDD tests are unit tests that follow the Red-Green-Refactor cycle. They test individual components in isolation.

### Running TDD Tests

```bash
# Run all TDD tests
make tdd

# Run specific TDD test categories
make tdd-field     # Field parsing tests
make tdd-header    # Header validation tests
make tdd-record    # Record operations tests
make tdd-error     # Error handling tests
make tdd-dbase3    # dBase III comprehensive tests

# Run TDD tests directly with unittest
python -m unittest discover tests -p "test_*_tdd.py" -v

# Run a specific TDD test file
python -m unittest tests.test_field_parsing_tdd -v
```

### TDD Test Files

- `test_field_parsing_tdd.py` - Tests for field parsing with edge cases
- `test_header_validation_tdd.py` - Header structure and validation tests
- `test_record_operations_tdd.py` - Record CRUD operations tests
- `test_error_handling_tdd.py` - Error scenarios and recovery tests
- `test_dbase3_comprehensive_tdd.py` - Comprehensive dBase III format tests

## BDD (Behavior-Driven Development) Tests

BDD tests use behave framework with Gherkin syntax to describe expected behaviors from a user perspective.

### Running BDD Tests

```bash
# Run all BDD tests
make bdd

# Run BDD tests with different options
make bdd-verbose    # Verbose output
make bdd-smoke      # Only critical smoke tests (@smoke tag)
make bdd-regression # Full regression suite (@regression tag)
make bdd-wip        # Work in progress tests (@wip tag)
make bdd-report     # Generate HTML report

# Run behave directly
behave

# Run specific feature files
behave features/dbf_operations.feature
behave features/dbase3_support.feature

# Run scenarios with specific tags
behave --tags=@critical
behave --tags=@smoke
behave --tags=@dbase3
```

### BDD Feature Files

Located in `features/` directory:
- `dbf_operations.feature` - DBF file creation, reading, writing operations
- `dbase3_support.feature` - dBase III format compatibility scenarios
- `error_handling.feature` - Error recovery and edge case scenarios
- `data_integrity.feature` - Data consistency and validation scenarios

### BDD Step Definitions

Step definitions are in `features/steps/dbf_steps.py` and connect Gherkin scenarios to actual test code.

## Running All Tests

```bash
# Run all tests (existing + TDD + BDD)
python -m unittest discover tests -v && make bdd

# Run traditional unit tests only
make test

# Run code coverage analysis
make coverage
```

## Test Organization

```
tests/
├── Traditional Tests (existing)
│   ├── test_dbfpy3.py
│   ├── test_fields.py
│   ├── test_code_page.py
│   ├── test_memo.py
│   └── test_dbase3.py
│
├── TDD Tests (new)
│   ├── test_field_parsing_tdd.py
│   ├── test_header_validation_tdd.py
│   ├── test_record_operations_tdd.py
│   ├── test_error_handling_tdd.py
│   └── test_dbase3_comprehensive_tdd.py
│
└── BDD Tests (behave)
    └── features/
        ├── dbf_operations.feature
        ├── dbase3_support.feature
        ├── error_handling.feature
        ├── data_integrity.feature
        ├── environment.py
        └── steps/
            └── dbf_steps.py
```

## Test Metrics

- **Traditional Tests**: 16 tests
- **TDD Tests**: 131 tests
- **BDD Scenarios**: 146 scenarios
- **Total Coverage**: Comprehensive coverage of all dbfpy3 functionality

## Continuous Integration

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run TDD Tests
  run: make tdd

- name: Run BDD Tests
  run: make bdd

- name: Generate Coverage Report
  run: make coverage
```

## Writing New Tests

### Adding TDD Tests

1. Create a new file following pattern: `test_<feature>_tdd.py`
2. Follow Red-Green-Refactor cycle:
   - Write failing test first
   - Implement minimal code to pass
   - Refactor while keeping tests green

### Adding BDD Scenarios

1. Add scenarios to existing `.feature` files or create new ones
2. Write in Gherkin syntax:
   ```gherkin
   Scenario: Your scenario name
     Given initial context
     When action is performed
     Then expected outcome
   ```
3. Implement step definitions in `features/steps/`

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're in the project root directory
2. **Missing behave**: Install with `pip install behave`
3. **Test failures**: Some TDD tests may fail initially (Red phase)
4. **Undefined steps**: BDD steps need implementation in step files

### Debug Options

```bash
# Run tests with Python debugger
python -m pdb -m unittest tests.test_field_parsing_tdd

# Run behave with debugging
behave --no-capture --no-capture-stderr

# Run specific test method
python -m unittest tests.test_field_parsing_tdd.TestFieldParsingTDD.test_parse_character_field
```

## Best Practices

1. **Run tests before commits**: Ensure all existing tests pass
2. **Use TDD for new features**: Write tests first, then implementation
3. **Use BDD for user stories**: Capture business requirements as scenarios
4. **Keep tests isolated**: Use temporary files and clean up resources
5. **Document test purposes**: Clear docstrings and comments

## Questions?

For more information about testing dbfpy3, see:
- `README_TESTS.md` - Detailed test documentation
- `BDD_IMPLEMENTATION_SUMMARY.md` - BDD framework details
- Individual test files for specific examples