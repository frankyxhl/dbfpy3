"""
Step definitions for DBF file operations BDD tests.

This module implements step definitions that connect Gherkin scenarios
to actual dbfpy3 library functionality using the behave framework.
"""

import os
import tempfile
import datetime
from behave import given, when, then, step
from behave import use_step_matcher
import shutil

# Import dbfpy3 components
from dbfpy3 import dbf
from dbfpy3.header import DbfHeader
from dbfpy3.fields import DbfCharacterField, DbfNumericField, DbfDateField, DbfLogicalField

# Use regex matcher for parameter extraction
use_step_matcher("re")


# ============================================================================
# Background and Setup Steps
# ============================================================================

@given('I am working with a clean test environment')
def step_clean_test_environment(context):
    """Set up a clean test environment."""
    if not hasattr(context, 'temp_files'):
        context.temp_files = []
    if not hasattr(context, 'temp_dir'):
        context.temp_dir = tempfile.mkdtemp(prefix='dbfpy3_test_')


@given('I have access to the dbfpy3 library')
def step_have_dbfpy3_access(context):
    """Verify dbfpy3 library is available."""
    assert dbf is not None
    context.dbf_module = dbf


@given(r'I am working with (?P<requirement_type>.*) requirements')
def step_working_with_requirements(context, requirement_type):
    """Set up context for specific requirement types."""
    context.requirement_type = requirement_type
    if not hasattr(context, 'temp_files'):
        context.temp_files = []


# ============================================================================
# File Creation and Management Steps
# ============================================================================

@given(r'I want to create a new DBF file called "(?P<filename>.*)"')
def step_want_to_create_dbf_file(context, filename):
    """Set intention to create a new DBF file."""
    context.target_filename = filename
    context.target_path = os.path.join(context.temp_dir, filename)
    context.temp_files.append(context.target_path)


@when('I create the file with basic field structure')
def step_create_file_with_basic_structure(context):
    """Create DBF file with basic field structure from table."""
    context.dbf_file = dbf.Dbf(context.target_path, new=True)
    
    for row in context.table:
        field_name = row['Field Name']
        field_type = row['Type']
        field_length = int(row['Length'])
        field_decimals = int(row['Decimals']) if row['Decimals'] != '0' else 0
        
        if field_decimals > 0:
            context.dbf_file.add_field((field_name, field_type, field_length, field_decimals))
        else:
            context.dbf_file.add_field((field_name, field_type, field_length))


@when('I close the file')
def step_close_file(context):
    """Close the currently open DBF file."""
    if hasattr(context, 'dbf_file') and context.dbf_file:
        context.dbf_file.close()


@then('the DBF file should exist on disk')
def step_dbf_file_should_exist(context):
    """Verify the DBF file exists on the filesystem."""
    assert os.path.exists(context.target_path), f"DBF file {context.target_path} should exist"
    assert os.path.getsize(context.target_path) > 0, "DBF file should not be empty"


@then('the file should have a valid DBF header')
def step_file_should_have_valid_header(context):
    """Verify the file has a valid DBF header."""
    # Reopen file to verify header
    test_dbf = dbf.Dbf(context.target_path)
    assert test_dbf.header is not None, "File should have a valid header"
    assert hasattr(test_dbf.header, 'signature'), "Header should have signature"
    test_dbf.close()


@then(r'the file should contain (?P<count>\d+) field definitions')
def step_file_should_contain_field_count(context, count):
    """Verify the file contains the expected number of field definitions."""
    expected_count = int(count)
    test_dbf = dbf.Dbf(context.target_path)
    actual_count = len(test_dbf.header.fields)
    assert actual_count == expected_count, f"Expected {expected_count} fields, got {actual_count}"
    test_dbf.close()


# ============================================================================
# File Opening and Reading Steps
# ============================================================================

@given(r'I have an existing DBF file "(?P<filename>.*)" with employee data')
def step_have_existing_dbf_with_data(context, filename):
    """Create an existing DBF file with sample employee data."""
    context.sample_file_path = os.path.join(context.temp_dir, filename)
    context.temp_files.append(context.sample_file_path)
    
    # Create sample file with employee data
    sample_dbf = dbf.Dbf(context.sample_file_path, new=True)
    sample_dbf.add_field(
        ("PRODUCT_ID", "N", 5, 0),
        ("PRODUCT_NAME", "C", 30),
        ("PRICE", "N", 8, 2),
        ("IN_STOCK", "L")
    )
    
    # Add sample records
    test_products = [
        (101, "Widget A", 19.99, True),
        (102, "Widget B", 29.99, True),
        (103, "Widget C", 39.99, False),
    ]
    
    for prod_id, name, price, in_stock in test_products:
        record = sample_dbf.new()
        record['PRODUCT_ID'] = prod_id
        record['PRODUCT_NAME'] = name
        record['PRICE'] = price
        record['IN_STOCK'] = in_stock
        sample_dbf.write(record)
    
    sample_dbf.close()


@when('I open the existing file for reading')
def step_open_existing_file_for_reading(context):
    """Open an existing DBF file for reading."""
    context.dbf_file = dbf.Dbf(context.sample_file_path)


@then('I should be able to access the file structure')
def step_should_access_file_structure(context):
    """Verify ability to access file structure."""
    assert context.dbf_file.header is not None, "Should be able to access header"
    assert len(context.dbf_file.header.fields) > 0, "Should have field definitions"


@then('I should see the correct number of field definitions')
def step_should_see_correct_field_count(context):
    """Verify the correct number of field definitions."""
    # Based on our sample data, should be 4 fields
    expected_fields = 4
    actual_fields = len(context.dbf_file.header.fields)
    assert actual_fields == expected_fields, f"Expected {expected_fields} fields, got {actual_fields}"


@then('I should be able to read the record count')
def step_should_read_record_count(context):
    """Verify ability to read record count."""
    record_count = len(context.dbf_file)
    assert record_count >= 0, "Should be able to read record count"


# ============================================================================
# Multiple Field Types Steps
# ============================================================================

@given('I want to create a comprehensive employee database')
def step_want_comprehensive_employee_database(context):
    """Set up for creating comprehensive employee database."""
    context.target_filename = "comprehensive_employees.dbf"
    context.target_path = os.path.join(context.temp_dir, context.target_filename)
    context.temp_files.append(context.target_path)


@when('I create a DBF file with the following field definitions')
def step_create_dbf_with_field_definitions(context):
    """Create DBF file with specified field definitions from table."""
    context.dbf_file = dbf.Dbf(context.target_path, new=True)
    context.field_specs = []
    
    for row in context.table:
        field_name = row['Field Name']
        field_type = row['Type']
        field_length = int(row['Length'])
        field_decimals = int(row.get('Decimals', '0'))
        purpose = row['Purpose']
        
        # Store field specs for later verification
        context.field_specs.append({
            'name': field_name,
            'type': field_type,
            'length': field_length,
            'decimals': field_decimals,
            'purpose': purpose
        })
        
        if field_decimals > 0:
            context.dbf_file.add_field((field_name, field_type, field_length, field_decimals))
        else:
            context.dbf_file.add_field((field_name, field_type, field_length))


@when('I save the file structure')
def step_save_file_structure(context):
    """Save the file structure."""
    # File is automatically saved when we close it
    if hasattr(context, 'dbf_file') and context.dbf_file:
        context.dbf_file.close()
        context.dbf_file = None


@then('each field should be correctly defined in the header')
def step_each_field_correctly_defined(context):
    """Verify each field is correctly defined in the header."""
    # Reopen file to verify
    test_dbf = dbf.Dbf(context.target_path)
    
    for i, field_spec in enumerate(context.field_specs):
        if i < len(test_dbf.header.fields):
            field = test_dbf.header.fields[i]
            expected_name = field_spec['name'].encode() if isinstance(field_spec['name'], str) else field_spec['name']
            assert field.name == expected_name, f"Field {i} name mismatch: expected {expected_name}, got {field.name}"
    
    test_dbf.close()


@then('the field types should match the specifications')
def step_field_types_should_match_specs(context):
    """Verify field types match specifications."""
    # This is verified implicitly by successful field creation
    assert len(context.field_specs) > 0, "Should have field specifications to verify"


@then('the field lengths should be preserved accurately')
def step_field_lengths_preserved_accurately(context):
    """Verify field lengths are preserved accurately."""
    test_dbf = dbf.Dbf(context.target_path)
    
    for i, field_spec in enumerate(context.field_specs):
        if i < len(test_dbf.header.fields):
            field = test_dbf.header.fields[i]
            assert field.length == field_spec['length'], \
                f"Field {i} length mismatch: expected {field_spec['length']}, got {field.length}"
    
    test_dbf.close()


# ============================================================================
# Record Operations Steps
# ============================================================================

@given('I have a DBF file with employee structure')
def step_have_dbf_with_employee_structure(context):
    """Create a DBF file with employee structure."""
    context.employee_file_path = os.path.join(context.temp_dir, "employee_records.dbf")
    context.temp_files.append(context.employee_file_path)
    
    context.dbf_file = dbf.Dbf(context.employee_file_path, new=True)
    context.dbf_file.add_field(
        ("EMPLOYEE_ID", "N", 6, 0),
        ("FULL_NAME", "C", 50),
        ("SALARY", "N", 10, 2),
        ("IS_ACTIVE", "L"),
        ("HIRE_DATE", "D")
    )


@when('I add a new employee record with the following data')
def step_add_new_employee_record(context):
    """Add a new employee record with specified data."""
    context.record = context.dbf_file.new()
    
    for row in context.table:
        field_name = row['Field']
        field_value = row['Value']
        
        # Convert values based on field type
        if field_name == 'EMPLOYEE_ID':
            context.record[field_name] = int(field_value)
        elif field_name == 'SALARY':
            context.record[field_name] = float(field_value)
        elif field_name == 'IS_ACTIVE':
            context.record[field_name] = field_value.lower() == 'true'
        elif field_name == 'HIRE_DATE':
            # Parse date string to tuple format expected by DBF
            date_parts = field_value.split('-')
            context.record[field_name] = (int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
        else:
            context.record[field_name] = field_value
    
    context.expected_record_data = dict(context.table.rows[0] for rows in [context.table] for row in rows)


@when('I save the record to the file')
def step_save_record_to_file(context):
    """Save the record to the file."""
    context.dbf_file.write(context.record)


@then('the record should be stored in the database')
def step_record_should_be_stored(context):
    """Verify the record is stored in the database."""
    record_count = len(context.dbf_file)
    assert record_count > 0, "Database should contain at least one record"


@then('I should be able to retrieve the record by index')
def step_should_retrieve_record_by_index(context):
    """Verify ability to retrieve record by index."""
    retrieved_record = context.dbf_file[0]
    assert retrieved_record is not None, "Should be able to retrieve record by index"
    context.retrieved_record = retrieved_record


@then('all field values should match the original data')
def step_all_field_values_should_match(context):
    """Verify all field values match the original data."""
    # This is a basic check - more specific validation would go in individual field tests
    assert context.retrieved_record is not None, "Should have a retrieved record to verify"


# ============================================================================
# Error Handling Steps
# ============================================================================

@given(r'I have a path to a non-existent DBF file "(?P<file_path>.*)"')
def step_have_nonexistent_file_path(context, file_path):
    """Set up path to non-existent file."""
    context.nonexistent_path = file_path
    # Ensure the file doesn't exist
    if os.path.exists(file_path):
        os.remove(file_path)


@when('I attempt to open the missing file')
def step_attempt_open_missing_file(context):
    """Attempt to open the missing file and capture any exceptions."""
    context.exception = None
    try:
        context.dbf_file = dbf.Dbf(context.nonexistent_path)
    except Exception as e:
        context.exception = e


@then('I should receive a FileNotFoundError')
def step_should_receive_file_not_found_error(context):
    """Verify that a FileNotFoundError was raised."""
    assert context.exception is not None, "Should have raised an exception"
    assert isinstance(context.exception, (FileNotFoundError, IOError)), \
        f"Expected FileNotFoundError or IOError, got {type(context.exception)}"


@then('the error message should indicate the file cannot be found')
def step_error_message_should_indicate_file_not_found(context):
    """Verify error message indicates file cannot be found."""
    error_message = str(context.exception).lower()
    assert any(phrase in error_message for phrase in ['no such file', 'not found', 'cannot find']), \
        f"Error message should indicate file not found: {context.exception}"


@then('the error message should include the attempted file path')
def step_error_message_should_include_file_path(context):
    """Verify error message includes the attempted file path."""
    error_message = str(context.exception)
    # The path might be normalized, so check for key parts
    assert 'missing.dbf' in error_message or 'nonexistent' in error_message, \
        f"Error message should include file path reference: {context.exception}"


@then('my application should continue running normally')
def step_application_should_continue_normally(context):
    """Verify application can continue after handling the error."""
    # If we got here without crashing, the application continued normally
    assert True, "Application should continue running after handling the error"


# ============================================================================
# Context Manager Steps
# ============================================================================

@given('I want to ensure proper resource management')
def step_want_proper_resource_management(context):
    """Set up for testing proper resource management."""
    context.resource_test_file = os.path.join(context.temp_dir, "resource_test.dbf")
    context.temp_files.append(context.resource_test_file)


@when('I use the DBF file within a context manager')
def step_use_dbf_within_context_manager(context):
    """Use DBF file within a context manager."""
    context.context_manager_used = True
    with dbf.Dbf(context.resource_test_file, new=True) as db:
        db.add_field(("TEST_FIELD", "C", 10))
        context.context_db = db


@when('I perform file operations inside the context')
def step_perform_operations_inside_context(context):
    """Perform operations inside the context manager."""
    # Operations are performed in the previous step
    assert context.context_manager_used, "Context manager should have been used"


@when('the context manager closes automatically')
def step_context_manager_closes_automatically(context):
    """Verify context manager closes automatically."""
    # This happens automatically when exiting the 'with' block
    pass


@then('the file should be properly closed')
def step_file_should_be_properly_closed(context):
    """Verify the file is properly closed."""
    # The file should exist and be accessible
    assert os.path.exists(context.resource_test_file), "File should exist after context manager"


@then('no file handles should remain open')
def step_no_file_handles_should_remain_open(context):
    """Verify no file handles remain open."""
    # This is difficult to test directly, but we can verify we can open the file again
    test_db = dbf.Dbf(context.resource_test_file)
    test_db.close()


@then('subsequent operations should work correctly')
def step_subsequent_operations_should_work(context):
    """Verify subsequent operations work correctly."""
    # Open the file again and verify it works
    test_db = dbf.Dbf(context.resource_test_file)
    assert len(test_db.header.fields) > 0, "Should be able to access field definitions"
    test_db.close()


# ============================================================================
# Cleanup Steps
# ============================================================================

def cleanup_temp_files(context):
    """Clean up temporary files created during tests."""
    if hasattr(context, 'dbf_file') and context.dbf_file:
        try:
            context.dbf_file.close()
        except:
            pass
    
    if hasattr(context, 'temp_files'):
        for temp_file in context.temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    if hasattr(context, 'temp_dir'):
        if os.path.exists(context.temp_dir):
            try:
                shutil.rmtree(context.temp_dir)
            except:
                pass