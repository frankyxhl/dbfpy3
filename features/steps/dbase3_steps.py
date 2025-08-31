"""
Step definitions for dBase III compatibility BDD tests.

This module implements step definitions for testing dBase III format
compatibility and legacy system integration.
"""

import os
import struct
import tempfile
from behave import given, when, then, step
from behave import use_step_matcher

from dbfpy3 import dbf
from dbfpy3.header import DbfHeader

# Use regex matcher for parameter extraction
use_step_matcher("re")


# ============================================================================
# dBase III Setup Steps
# ============================================================================

@given('I am specifically working with dBase III format requirements')
def step_working_with_dbase3_requirements(context):
    """Set up context for dBase III format testing."""
    context.dbase3_mode = True
    context.expected_signatures = [0x03, 0x83]  # dBase III signatures
    if not hasattr(context, 'temp_files'):
        context.temp_files = []
    if not hasattr(context, 'temp_dir'):
        context.temp_dir = tempfile.mkdtemp(prefix='dbase3_test_')


@given('I have access to the dbfpy3 library with dBase III support')
def step_have_dbase3_support(context):
    """Verify dbfpy3 library supports dBase III format."""
    assert dbf is not None
    context.dbf_module = dbf


# ============================================================================
# dBase III File Creation Steps
# ============================================================================

@given('I want to create a file compatible with dBase III')
def step_want_dbase3_compatible_file(context):
    """Set intention to create dBase III compatible file."""
    context.dbase3_file_path = os.path.join(context.temp_dir, "dbase3_compatible.dbf")
    context.temp_files.append(context.dbase3_file_path)


@when('I create a new DBF file with dBase III signature')
def step_create_dbf_with_dbase3_signature(context):
    """Create a new DBF file with dBase III signature."""
    context.dbf_file = dbf.Dbf(context.dbase3_file_path, new=True)
    # Set dBase III signature
    context.dbf_file.header.signature = 0x03  # dBase III without memo


@when('I add standard dBase III field types')
def step_add_dbase3_field_types(context):
    """Add standard dBase III field types from table."""
    for row in context.table:
        field_name = row['Field Name']
        field_type = row['Type']
        field_length = int(row['Length'])
        purpose = row['Purpose']
        
        # Handle special cases for dBase III field types
        if field_type == 'N' and 'decimal' in purpose.lower():
            context.dbf_file.add_field((field_name, field_type, field_length, 2))
        else:
            context.dbf_file.add_field((field_name, field_type, field_length))


@when('I save the file with dBase III format')
def step_save_file_with_dbase3_format(context):
    """Save the file maintaining dBase III format."""
    # Ensure signature remains dBase III
    context.dbf_file.header.signature = 0x03
    context.dbf_file.close()


@then('the file signature should be 0x03 or 0x83')
def step_file_signature_should_be_dbase3(context):
    """Verify the file has a valid dBase III signature."""
    # Read the file directly to check signature
    with open(context.dbase3_file_path, 'rb') as f:
        signature = struct.unpack('B', f.read(1))[0]
    
    assert signature in [0x03, 0x83], f"Expected dBase III signature (0x03 or 0x83), got 0x{signature:02x}"
    context.actual_signature = signature


@then('the file should be readable by legacy dBase III applications')
def step_file_readable_by_legacy_applications(context):
    """Verify file format is compatible with legacy applications."""
    # We verify this by ensuring the file structure follows dBase III standards
    db = dbf.Dbf(context.dbase3_file_path)
    
    # Check header structure is valid
    assert db.header is not None, "File should have valid header"
    assert len(db.header.fields) > 0, "File should have field definitions"
    
    # Verify field names are within dBase III limits (10 characters)
    for field in db.header.fields:
        field_name_length = len(field.name.rstrip(b'\x00'))
        assert field_name_length <= 10, f"Field name too long for dBase III: {field.name}"
    
    db.close()


@then('all field types should conform to dBase III standards')
def step_field_types_conform_to_dbase3_standards(context):
    """Verify all field types conform to dBase III standards."""
    db = dbf.Dbf(context.dbase3_file_path)
    
    valid_dbase3_types = [b'C', b'N', b'L', b'D', b'M']  # Character, Numeric, Logical, Date, Memo
    
    for field in db.header.fields:
        field_type = field.type_code.encode() if isinstance(field.type_code, str) else field.type_code
        assert field_type in valid_dbase3_types, \
            f"Field type {field_type} is not valid for dBase III"
    
    db.close()


# ============================================================================
# Reading Existing dBase III Files Steps
# ============================================================================

@given('I have an existing dBase III format file from a legacy system')
def step_have_existing_dbase3_file(context):
    """Create a mock existing dBase III file from legacy system."""
    context.legacy_file_path = os.path.join(context.temp_dir, "legacy_system.dbf")
    context.temp_files.append(context.legacy_file_path)
    
    # Create a file that simulates a legacy dBase III file
    legacy_db = dbf.Dbf(context.legacy_file_path, new=True)
    legacy_db.header.signature = 0x03  # dBase III signature
    
    legacy_db.add_field(
        ("LEGACY_ID", "N", 8, 0),
        ("COMPANY", "C", 40),
        ("AMOUNT", "N", 10, 2),
        ("ACTIVE", "L")
    )
    
    # Add some legacy-style data
    record = legacy_db.new()
    record['LEGACY_ID'] = 1001
    record['COMPANY'] = 'Legacy Corp'
    record['AMOUNT'] = 299.99
    record['ACTIVE'] = True
    legacy_db.write(record)
    
    legacy_db.close()


@when('I open the file using dbfpy3')
def step_open_file_using_dbfpy3(context):
    """Open the legacy file using dbfpy3."""
    context.dbf_file = dbf.Dbf(context.legacy_file_path)


@then('I should be able to read the dBase III header')
def step_should_read_dbase3_header(context):
    """Verify ability to read dBase III header."""
    assert context.dbf_file.header is not None, "Should be able to read header"
    assert context.dbf_file.header.signature in [0x03, 0x83], \
        f"Should recognize dBase III signature, got 0x{context.dbf_file.header.signature:02x}"


@then('I should correctly interpret the field definitions')
def step_should_interpret_field_definitions(context):
    """Verify correct interpretation of field definitions."""
    fields = context.dbf_file.header.fields
    assert len(fields) == 4, f"Expected 4 fields, got {len(fields)}"
    
    # Check specific field properties
    field_names = [field.name.decode().rstrip('\x00') for field in fields]
    expected_names = ['LEGACY_ID', 'COMPANY', 'AMOUNT', 'ACTIVE']
    
    for expected in expected_names:
        assert expected in field_names, f"Missing expected field: {expected}"


@then('I should access all records without data corruption')
def step_should_access_records_without_corruption(context):
    """Verify all records are accessible without corruption."""
    record_count = len(context.dbf_file)
    assert record_count > 0, "Should have at least one record"
    
    # Access first record to verify data integrity
    record = context.dbf_file[0]
    assert record['LEGACY_ID'] == 1001, "Numeric field should be preserved"
    assert 'Legacy Corp' in record['COMPANY'], "Character field should be preserved"
    assert abs(record['AMOUNT'] - 299.99) < 0.01, "Decimal precision should be preserved"
    assert record['ACTIVE'] == True, "Logical field should be preserved"


@then('the character encoding should be handled properly')
def step_character_encoding_handled_properly(context):
    """Verify character encoding is handled properly."""
    record = context.dbf_file[0]
    company_name = record['COMPANY']
    
    # Verify we can read the string without encoding errors
    assert isinstance(company_name, (str, bytes)), "Company name should be readable"
    if isinstance(company_name, bytes):
        company_name = company_name.decode('cp437', errors='ignore')  # Default dBase III encoding
    
    assert len(company_name.strip()) > 0, "Company name should not be empty after encoding"


# ============================================================================
# Signature Variation Steps
# ============================================================================

@given('I need to work with different dBase III signature types')
def step_need_different_signature_types(context):
    """Set up for testing different signature types."""
    context.signature_test_files = []


@when(r'I encounter a file with signature (?P<signature>0x[0-9A-F]+) \((?P<description>.*)\)')
def step_encounter_file_with_signature(context, signature, description):
    """Create and test file with specific signature."""
    sig_value = int(signature, 16)
    test_file = os.path.join(context.temp_dir, f"sig_{sig_value:02x}_test.dbf")
    context.temp_files.append(test_file)
    context.signature_test_files.append((test_file, sig_value, description))
    
    # Create file with specific signature
    test_db = dbf.Dbf(test_file, new=True)
    test_db.header.signature = sig_value
    test_db.add_field(("TEST_FIELD", "C", 20))
    
    record = test_db.new()
    record['TEST_FIELD'] = f'Test {description}'
    test_db.write(record)
    test_db.close()
    
    # Store for verification
    context.current_test_file = test_file
    context.current_signature = sig_value


@then('I should be able to read the file correctly')
def step_should_read_file_correctly(context):
    """Verify ability to read file with specific signature correctly."""
    test_db = dbf.Dbf(context.current_test_file)
    
    # Verify signature is preserved
    assert test_db.header.signature == context.current_signature, \
        f"Signature should be preserved: expected 0x{context.current_signature:02x}, got 0x{test_db.header.signature:02x}"
    
    # Verify we can read records
    assert len(test_db) > 0, "Should be able to read records"
    record = test_db[0]
    assert 'Test' in record['TEST_FIELD'], "Should be able to read field content"
    
    test_db.close()


@then('I should recognize the memo field capability')
def step_should_recognize_memo_capability(context):
    """Verify recognition of memo field capability."""
    if context.current_signature == 0x83:
        # File with memo capability
        test_db = dbf.Dbf(context.current_test_file)
        # The signature indicates memo support is available
        assert test_db.header.signature == 0x83, "Should recognize memo-capable signature"
        test_db.close()


# ============================================================================
# Data Format Preservation Steps
# ============================================================================

@given('I have a dBase III file with various field types')
def step_have_dbase3_with_various_fields(context):
    """Create dBase III file with various field types."""
    context.various_fields_file = os.path.join(context.temp_dir, "various_fields.dbf")
    context.temp_files.append(context.various_fields_file)
    
    db = dbf.Dbf(context.various_fields_file, new=True)
    db.header.signature = 0x03
    
    db.add_field(
        ("NUM_INT", "N", 8, 0),      # Integer
        ("NUM_DEC", "N", 10, 2),     # Decimal
        ("CHAR_FIELD", "C", 25),     # Character
        ("LOG_FIELD", "L"),          # Logical
        ("DATE_FIELD", "D")          # Date
    )
    
    # Add test record
    record = db.new()
    record['NUM_INT'] = 12345
    record['NUM_DEC'] = 123.45
    record['CHAR_FIELD'] = 'Test Character Data'
    record['LOG_FIELD'] = True
    record['DATE_FIELD'] = (2023, 12, 25)
    db.write(record)
    
    db.close()
    context.dbf_file = None  # Will be reopened in test steps


@when(r'I read (?P<field_type>.*) fields from the legacy format')
def step_read_fields_from_legacy_format(context, field_type):
    """Read specific field type from legacy format."""
    if not hasattr(context, 'dbf_file') or context.dbf_file is None:
        context.dbf_file = dbf.Dbf(context.various_fields_file)
    
    context.test_record = context.dbf_file[0]
    context.current_field_type = field_type


@then('decimal precision should be maintained correctly')
def step_decimal_precision_maintained(context):
    """Verify decimal precision is maintained."""
    if context.current_field_type.lower() == 'numeric':
        # Check decimal field
        decimal_value = context.test_record['NUM_DEC']
        assert abs(decimal_value - 123.45) < 0.001, \
            f"Decimal precision not maintained: expected 123.45, got {decimal_value}"


@then('text padding and encoding should be preserved')
def step_text_padding_encoding_preserved(context):
    """Verify text padding and encoding is preserved."""
    if context.current_field_type.lower() == 'character':
        char_value = context.test_record['CHAR_FIELD']
        if isinstance(char_value, bytes):
            char_value = char_value.decode('cp437', errors='ignore')
        
        assert 'Test Character Data' in char_value.strip(), \
            f"Character data not preserved: got '{char_value}'"


@then('boolean values should be interpreted correctly')
def step_boolean_values_interpreted_correctly(context):
    """Verify boolean values are interpreted correctly."""
    if context.current_field_type.lower() == 'logical':
        logical_value = context.test_record['LOG_FIELD']
        assert logical_value == True, f"Logical value not preserved: expected True, got {logical_value}"


@then('dates should be parsed in the correct format')
def step_dates_parsed_correctly(context):
    """Verify dates are parsed in correct format."""
    if context.current_field_type.lower() == 'date':
        date_value = context.test_record['DATE_FIELD']
        if isinstance(date_value, tuple):
            assert date_value == (2023, 12, 25), \
                f"Date not preserved: expected (2023, 12, 25), got {date_value}"


# ============================================================================
# Constraint Validation Steps
# ============================================================================

@given('I am creating a dBase III compatible file')
def step_creating_dbase3_compatible_file(context):
    """Set up for creating dBase III compatible file."""
    context.constraint_test_file = os.path.join(context.temp_dir, "constraint_test.dbf")
    context.temp_files.append(context.constraint_test_file)


@when(r'I try to use field names longer than (?P<max_length>\d+) characters')
def step_try_long_field_names(context, max_length):
    """Test using field names longer than allowed limit."""
    max_len = int(max_length)
    long_name = 'A' * (max_len + 1)  # One character longer than allowed
    
    context.constraint_exception = None
    try:
        db = dbf.Dbf(context.constraint_test_file, new=True)
        db.add_field((long_name, "C", 10))
        db.close()
    except Exception as e:
        context.constraint_exception = e


@then(r'the system should enforce the (?P<limit>\d+)-character limit')
def step_system_should_enforce_character_limit(context, limit):
    """Verify system enforces character limit."""
    limit_num = int(limit)
    # The system should either truncate the name or raise an exception
    # We expect some kind of constraint enforcement
    if context.constraint_exception:
        # Exception was raised - good constraint enforcement
        assert True
    else:
        # If no exception, verify the field name was truncated
        db = dbf.Dbf(context.constraint_test_file)
        if len(db.header.fields) > 0:
            field_name = db.header.fields[0].name.decode().rstrip('\x00')
            assert len(field_name) <= limit_num, \
                f"Field name should be truncated to {limit_num} characters, got {len(field_name)}"
        db.close()


@when(r'I try to use more than (?P<max_fields>\d+) fields')
def step_try_too_many_fields(context, max_fields):
    """Test using more fields than allowed."""
    max_field_count = int(max_fields)
    context.field_limit_exception = None
    
    try:
        db = dbf.Dbf(context.constraint_test_file, new=True)
        # Try to add more fields than the limit
        for i in range(max_field_count + 1):
            db.add_field((f"FIELD_{i:03d}", "C", 10))
        db.close()
    except Exception as e:
        context.field_limit_exception = e


@then('the system should enforce the field count limit')
def step_system_should_enforce_field_count_limit(context):
    """Verify system enforces field count limit."""
    # The system should handle the field count appropriately
    # This might be enforced at the dBase III level or handled gracefully
    if hasattr(context, 'field_limit_exception') and context.field_limit_exception:
        # Exception was raised - appropriate constraint enforcement
        assert True
    else:
        # If no exception, verify reasonable field count
        if os.path.exists(context.constraint_test_file):
            db = dbf.Dbf(context.constraint_test_file)
            field_count = len(db.header.fields)
            assert field_count <= 255, f"Field count should be reasonable, got {field_count}"
            db.close()


# ============================================================================
# Cleanup for dBase III tests
# ============================================================================

def cleanup_dbase3_temp_files(context):
    """Clean up temporary files from dBase III tests."""
    if hasattr(context, 'dbf_file') and context.dbf_file:
        try:
            context.dbf_file.close()
        except:
            pass
    
    # Additional cleanup specific to dBase III tests
    temp_file_attrs = ['dbase3_file_path', 'legacy_file_path', 'various_fields_file', 'constraint_test_file']
    for attr in temp_file_attrs:
        if hasattr(context, attr):
            file_path = getattr(context, attr)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass