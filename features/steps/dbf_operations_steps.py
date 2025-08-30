"""
Step definitions for DBF file operations with corrected field format.
"""

import os
import tempfile
import datetime
from behave import given, when, then

from dbfpy3 import dbf


@given('I am working with a clean test environment')
def step_clean_test_environment(context):
    """Set up a clean test environment."""
    context.temp_dir = tempfile.mkdtemp(prefix='dbfpy3_bdd_')
    context.temp_files = []


@given('I have access to the dbfpy3 library')
def step_have_dbfpy3_access(context):
    """Verify dbfpy3 library is available."""
    assert dbf is not None


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
        field_type = row['Type']
        field_name = row['Field Name']
        field_length = int(row['Length'])
        field_decimals = int(row['Decimals']) if row['Decimals'] != '0' else 0
        
        if field_decimals > 0:
            context.dbf_file.add_field((field_type, field_name, field_length, field_decimals))
        else:
            context.dbf_file.add_field((field_type, field_name, field_length))


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


def cleanup_temp_files(context):
    """Clean up temporary files."""
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
    
    if hasattr(context, 'temp_dir') and os.path.exists(context.temp_dir):
        try:
            import shutil
            shutil.rmtree(context.temp_dir)
        except:
            pass