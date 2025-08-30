"""
Simple step definitions for basic DBF functionality testing.
"""

import os
import tempfile
from behave import given, when, then

# Import dbfpy3 
from dbfpy3 import dbf


@given('I have the dbfpy3 library available')
def step_have_dbfpy3_available(context):
    """Verify dbfpy3 library is available."""
    context.temp_dir = tempfile.mkdtemp(prefix='simple_dbf_test_')
    context.test_file = os.path.join(context.temp_dir, 'test.dbf')
    assert dbf is not None, "dbfpy3 should be available"


@when('I create a new DBF file with fields')
def step_create_dbf_with_fields(context):
    """Create a new DBF file with basic fields."""
    context.dbf_file = dbf.Dbf(context.test_file, new=True)
    context.dbf_file.add_field(
        ("N", "ID", 5, 0),
        ("C", "NAME", 30)
    )


@when('I add a simple record')
def step_add_simple_record(context):
    """Add a simple record to the DBF file."""
    record = context.dbf_file.new()
    record['ID'] = 1
    record['NAME'] = 'Test Record'
    context.dbf_file.write(record)


# Removed duplicate step - using the one from dbf_operations_steps.py


@then('the file should exist and be readable')
def step_file_should_exist_and_readable(context):
    """Verify the file exists and is readable."""
    assert os.path.exists(context.test_file), "DBF file should exist"
    
    # Try to read the file back
    read_dbf = dbf.Dbf(context.test_file)
    assert len(read_dbf) == 1, "Should have one record"
    
    record = read_dbf[0]
    assert record['ID'] == 1, "ID should be 1"
    assert 'Test Record' in record['NAME'], "NAME should contain 'Test Record'"
    
    read_dbf.close()
    
    # Cleanup
    try:
        os.remove(context.test_file)
        os.rmdir(context.temp_dir)
    except:
        pass