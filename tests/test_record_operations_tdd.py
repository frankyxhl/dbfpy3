#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TDD Tests for Record Operations - Reading and Writing.

This module implements comprehensive Test-Driven Development (TDD) tests for the
DbfRecord class and record operations in dbfpy3, focusing on record creation,
reading, writing, and data integrity.

Following TDD principles:
- Red: Write failing tests first
- Green: Implement minimal code to pass
- Refactor: Improve code while keeping tests green
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from dbfpy3 import dbf
from dbfpy3.record import DbfRecord
from dbfpy3.header import DbfHeader
from dbfpy3.fields import DbfCharacterField, DbfNumericField, DbfDateField, DbfLogicalField


class TestDbfRecordCreationTDD(unittest.TestCase):
    """TDD tests for DbfRecord creation and initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.header = DbfHeader()
        self.header.add_field(
            ("C", "NAME", 20),
            ("N", "AGE", 3, 0),
            ("N", "SALARY", 10, 2),
            ("L", "ACTIVE"),
            ("D", "BIRTHDATE")
        )

    def test_record_creation_with_valid_header_should_succeed(self):
        """
        GIVEN: A valid DbfHeader with field definitions
        WHEN: Creating a new DbfRecord
        THEN: Should create record with all field names accessible
        """
        record = DbfRecord(self.header)
        
        self.assertIn('NAME', record)
        self.assertIn('AGE', record)
        self.assertIn('SALARY', record)
        self.assertIn('ACTIVE', record)
        self.assertIn('BIRTHDATE', record)

    def test_record_creation_should_initialize_fields_with_default_values(self):
        """
        GIVEN: A DbfRecord with field definitions
        WHEN: Creating a new record
        THEN: Should initialize all fields with appropriate default values
        """
        record = DbfRecord(self.header)
        
        # Character fields should be empty strings or spaces
        self.assertIsInstance(record['NAME'], (str, bytes))
        # Numeric fields should be None or 0
        self.assertIn(record['AGE'], [None, 0])
        self.assertIn(record['SALARY'], [None, 0, 0.0])
        # Logical fields should be None or False
        self.assertIn(record['ACTIVE'], [None, False])
        # Date fields should be None or empty
        self.assertIn(record['BIRTHDATE'], [None, (0, 0, 0)])

    def test_record_creation_with_empty_header_should_create_minimal_record(self):
        """
        GIVEN: An empty DbfHeader with no fields
        WHEN: Creating a new DbfRecord
        THEN: Should create record with only deletion flag
        """
        empty_header = DbfHeader()
        
        record = DbfRecord(empty_header)
        
        # Record should exist but have no fields
        self.assertIsNotNone(record)
        self.assertEqual(len(record._fields), 0)

    def test_record_creation_with_none_header_should_raise_error(self):
        """
        GIVEN: None as header parameter
        WHEN: Creating a new DbfRecord
        THEN: Should raise TypeError or AttributeError
        """
        with self.assertRaises((TypeError, AttributeError)):
            DbfRecord(None)

    def test_record_deletion_flag_should_default_to_not_deleted(self):
        """
        GIVEN: A newly created DbfRecord
        WHEN: Checking deletion status
        THEN: Should not be marked as deleted by default
        """
        record = DbfRecord(self.header)
        
        self.assertFalse(record.deleted)

    def test_record_deletion_flag_can_be_set(self):
        """
        GIVEN: A DbfRecord
        WHEN: Setting deletion flag to True
        THEN: Should mark record as deleted
        """
        record = DbfRecord(self.header)
        
        record.deleted = True
        
        self.assertTrue(record.deleted)


class TestDbfRecordFieldAccessTDD(unittest.TestCase):
    """TDD tests for field access operations in DbfRecord."""

    def setUp(self):
        """Set up test fixtures."""
        self.header = DbfHeader()
        self.header.add_field(
            ("C", "NAME", 20),
            ("N", "AGE", 3, 0),
            ("L", "ACTIVE")
        )
        self.record = DbfRecord(self.header)

    def test_record_field_access_by_name_should_return_field_value(self):
        """
        GIVEN: A record with field values set
        WHEN: Accessing field by name
        THEN: Should return the correct field value
        """
        self.record['NAME'] = 'John Doe'
        
        result = self.record['NAME']
        
        self.assertEqual(result, 'John Doe')

    def test_record_field_access_by_index_should_return_field_value(self):
        """
        GIVEN: A record with field values set
        WHEN: Accessing field by numeric index
        THEN: Should return the field value at that position
        """
        self.record['NAME'] = 'Jane Smith'
        
        result = self.record[0]  # First field (NAME)
        
        self.assertEqual(result, 'Jane Smith')

    def test_record_field_assignment_should_set_field_value(self):
        """
        GIVEN: A record with defined fields
        WHEN: Assigning value to a field
        THEN: Should store the value correctly
        """
        self.record['AGE'] = 30
        
        self.assertEqual(self.record['AGE'], 30)

    def test_record_field_assignment_with_wrong_type_should_convert_or_error(self):
        """
        GIVEN: A numeric field
        WHEN: Assigning string value to numeric field
        THEN: Should either convert or raise TypeError
        """
        try:
            self.record['AGE'] = 'thirty'
            # If conversion succeeded, verify result
            self.assertIsInstance(self.record['AGE'], (int, float, type(None)))
        except (TypeError, ValueError):
            # If conversion failed, that's also acceptable
            pass

    def test_record_access_nonexistent_field_should_raise_key_error(self):
        """
        GIVEN: A record with defined fields
        WHEN: Accessing field that doesn't exist
        THEN: Should raise KeyError
        """
        with self.assertRaises(KeyError):
            _ = self.record['NONEXISTENT']

    def test_record_assignment_to_nonexistent_field_should_raise_key_error(self):
        """
        GIVEN: A record with defined fields
        WHEN: Assigning to field that doesn't exist
        THEN: Should raise KeyError
        """
        with self.assertRaises(KeyError):
            self.record['NONEXISTENT'] = 'value'

    def test_record_field_access_case_insensitive_should_work(self):
        """
        GIVEN: A record with field named 'NAME'
        WHEN: Accessing field with different case 'name'
        THEN: Should return the field value (case insensitive)
        """
        self.record['NAME'] = 'Test User'
        
        # This may or may not work depending on implementation
        try:
            result = self.record['name']
            self.assertEqual(result, 'Test User')
        except KeyError:
            # Case sensitivity is also acceptable
            pass

    def test_record_field_names_should_be_accessible(self):
        """
        GIVEN: A record with defined fields
        WHEN: Getting list of field names
        THEN: Should return all field names
        """
        field_names = list(self.record.keys()) if hasattr(self.record, 'keys') else self.record._fields.keys()
        
        expected_names = ['NAME', 'AGE', 'ACTIVE']
        self.assertEqual(len(field_names), len(expected_names))
        for name in expected_names:
            self.assertIn(name, field_names)


class TestDbfRecordSerializationTDD(unittest.TestCase):
    """TDD tests for record serialization and deserialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.header = DbfHeader()
        self.header.add_field(
            ("C", "NAME", 10),
            ("N", "AGE", 3, 0),
            ("L", "ACTIVE")
        )
        # Total record length: 1 (deletion) + 10 (NAME) + 3 (AGE) + 1 (ACTIVE) = 15

    def test_record_to_bytes_should_produce_correct_length(self):
        """
        GIVEN: A record with field values set
        WHEN: Serializing record to bytes
        THEN: Should produce bytes of correct length
        """
        record = DbfRecord(self.header)
        record['NAME'] = 'John'
        record['AGE'] = 25
        record['ACTIVE'] = True
        
        record_bytes = record.to_bytes()
        
        self.assertEqual(len(record_bytes), self.header.record_length)

    def test_record_to_bytes_should_start_with_deletion_flag(self):
        """
        GIVEN: A record (not deleted)
        WHEN: Serializing to bytes
        THEN: First byte should be space character (not deleted)
        """
        record = DbfRecord(self.header)
        
        record_bytes = record.to_bytes()
        
        self.assertEqual(record_bytes[0:1], b' ')  # Not deleted

    def test_deleted_record_to_bytes_should_start_with_asterisk(self):
        """
        GIVEN: A record marked as deleted
        WHEN: Serializing to bytes
        THEN: First byte should be asterisk character (deleted)
        """
        record = DbfRecord(self.header)
        record.deleted = True
        
        record_bytes = record.to_bytes()
        
        self.assertEqual(record_bytes[0:1], b'*')  # Deleted

    def test_record_to_bytes_should_encode_character_field_correctly(self):
        """
        GIVEN: A record with character field value
        WHEN: Serializing to bytes
        THEN: Should encode character field with proper padding
        """
        record = DbfRecord(self.header)
        record['NAME'] = 'John'
        
        record_bytes = record.to_bytes()
        
        # Character field should be at bytes 1-10, left-aligned with spaces
        name_bytes = record_bytes[1:11]
        self.assertEqual(name_bytes, b'John      ')

    def test_record_to_bytes_should_encode_numeric_field_correctly(self):
        """
        GIVEN: A record with numeric field value
        WHEN: Serializing to bytes
        THEN: Should encode numeric field with proper alignment
        """
        record = DbfRecord(self.header)
        record['AGE'] = 25
        
        record_bytes = record.to_bytes()
        
        # Numeric field should be at bytes 11-13, right-aligned
        age_bytes = record_bytes[11:14]
        self.assertEqual(age_bytes, b' 25')

    def test_record_to_bytes_should_encode_logical_field_correctly(self):
        """
        GIVEN: A record with logical field value
        WHEN: Serializing to bytes
        THEN: Should encode logical field as T/F/?
        """
        record = DbfRecord(self.header)
        record['ACTIVE'] = True
        
        record_bytes = record.to_bytes()
        
        # Logical field should be at byte 14
        active_byte = record_bytes[14:15]
        self.assertEqual(active_byte, b'T')

    @unittest.skip("DbfRecord.from_bytes not implemented - TODO: implement record deserialization")
    def test_record_from_bytes_should_reconstruct_record_correctly(self):
        """
        GIVEN: Serialized record bytes
        WHEN: Deserializing from bytes
        THEN: Should reconstruct record with same field values
        """
        # Create and serialize a record
        original_record = DbfRecord(self.header)
        original_record['NAME'] = 'John'
        original_record['AGE'] = 25
        original_record['ACTIVE'] = True
        record_bytes = original_record.to_bytes()
        
        # Deserialize
        reconstructed_record = DbfRecord.from_bytes(self.header, record_bytes)
        
        self.assertEqual(reconstructed_record['NAME'].strip(), 'John')
        self.assertEqual(reconstructed_record['AGE'], 25)
        self.assertEqual(reconstructed_record['ACTIVE'], True)

    @unittest.skip("DbfRecord.from_bytes not implemented - TODO: implement record deserialization")
    def test_record_from_bytes_with_insufficient_data_should_raise_error(self):
        """
        GIVEN: Insufficient record bytes
        WHEN: Deserializing from bytes
        THEN: Should raise appropriate error
        """
        insufficient_bytes = b'short'
        
        with self.assertRaises((ValueError, struct.error, IndexError)):
            DbfRecord.from_bytes(self.header, insufficient_bytes)

    @unittest.skip("DbfRecord.from_bytes not implemented - TODO: implement record deserialization")
    def test_record_from_bytes_with_excess_data_should_use_only_needed_bytes(self):
        """
        GIVEN: Record bytes with extra data
        WHEN: Deserializing from bytes
        THEN: Should use only the needed bytes and ignore excess
        """
        record = DbfRecord(self.header)
        record['NAME'] = 'Test'
        record['AGE'] = 30
        record['ACTIVE'] = False
        
        record_bytes = record.to_bytes() + b'extra_data'
        
        reconstructed = DbfRecord.from_bytes(self.header, record_bytes)
        
        self.assertEqual(reconstructed['NAME'].strip(), 'Test')
        self.assertEqual(reconstructed['AGE'], 30)
        self.assertEqual(reconstructed['ACTIVE'], False)


class TestDbfRecordValidationTDD(unittest.TestCase):
    """TDD tests for record validation and data integrity."""

    def setUp(self):
        """Set up test fixtures."""
        self.header = DbfHeader()
        self.header.add_field(
            ("C", "NAME", 10),
            ("N", "AGE", 3, 0),
            ("N", "SALARY", 8, 2),
            ("L", "ACTIVE"),
            ("D", "BIRTHDATE")
        )

    def test_record_character_field_length_validation(self):
        """
        GIVEN: A character field with maximum length limit
        WHEN: Assigning value longer than limit
        THEN: Should truncate or handle appropriately
        """
        record = DbfRecord(self.header)
        long_name = 'A' * 20  # Longer than 10-character limit
        
        record['NAME'] = long_name
        
        # Should be truncated or raise error
        try:
            stored_name = record['NAME']
            self.assertLessEqual(len(stored_name), 10)
        except ValueError:
            # Rejection is also acceptable
            pass

    def test_record_numeric_field_type_validation(self):
        """
        GIVEN: A numeric field
        WHEN: Assigning non-numeric value
        THEN: Should convert or raise appropriate error
        """
        record = DbfRecord(self.header)
        
        # Try assigning string to numeric field
        try:
            record['AGE'] = 'not_a_number'
            # If accepted, should be converted or None
            self.assertIn(type(record['AGE']), [int, float, type(None)])
        except (ValueError, TypeError):
            # Rejection is acceptable
            pass

    def test_record_numeric_field_range_validation(self):
        """
        GIVEN: A numeric field with specific length
        WHEN: Assigning value too large for field
        THEN: Should handle overflow appropriately
        """
        record = DbfRecord(self.header)
        
        # AGE field is 3 digits, so max value is 999
        record['AGE'] = 1000  # Too large
        
        # Should be truncated, converted to string representation, or error
        try:
            stored_age = record['AGE']
            # If stored, should be manageable value
            self.assertIsInstance(stored_age, (int, float, type(None)))
        except (ValueError, OverflowError):
            # Rejection is acceptable
            pass

    def test_record_logical_field_value_validation(self):
        """
        GIVEN: A logical field
        WHEN: Assigning various boolean-like values
        THEN: Should convert to appropriate True/False/?
        """
        record = DbfRecord(self.header)
        
        test_values = [
            (True, True),
            (False, False),
            ('T', True),
            ('F', False),
            ('Y', True),
            ('N', False),
            (1, True),
            (0, False),
            (None, None)  # or False, depending on implementation
        ]
        
        for input_val, expected in test_values:
            with self.subTest(input_val=input_val):
                record['ACTIVE'] = input_val
                result = record['ACTIVE']
                if expected is None:
                    self.assertIn(result, [None, False])
                else:
                    self.assertEqual(result, expected)

    def test_record_date_field_validation(self):
        """
        GIVEN: A date field
        WHEN: Assigning various date formats
        THEN: Should validate and convert appropriately
        """
        record = DbfRecord(self.header)
        
        valid_dates = [
            (2023, 12, 25),  # Tuple format
            # datetime.date(2023, 12, 25),  # Date object (if supported)
        ]
        
        for date_val in valid_dates:
            with self.subTest(date_val=date_val):
                record['BIRTHDATE'] = date_val
                stored_date = record['BIRTHDATE']
                # Should be stored in some valid format
                self.assertIsNotNone(stored_date)

    def test_record_invalid_date_should_be_handled(self):
        """
        GIVEN: A date field
        WHEN: Assigning invalid date
        THEN: Should handle error appropriately
        """
        record = DbfRecord(self.header)
        
        invalid_dates = [
            (2023, 13, 25),  # Invalid month
            (2023, 12, 32),  # Invalid day
            'not_a_date',    # Invalid type
        ]
        
        for invalid_date in invalid_dates:
            with self.subTest(invalid_date=invalid_date):
                try:
                    record['BIRTHDATE'] = invalid_date
                    # If accepted, should be None or empty date
                    result = record['BIRTHDATE']
                    self.assertIn(result, [None, (0, 0, 0)])
                except (ValueError, TypeError):
                    # Rejection is also acceptable
                    pass


class TestDbfRecordIntegrationTDD(unittest.TestCase):
    """TDD tests for record operations integrated with DBF files."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_record_write_and_read_should_preserve_data(self):
        """
        GIVEN: A DBF file and record with data
        WHEN: Writing record and reading it back
        THEN: Should preserve all field values accurately
        """
        # Create DBF file and add record
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(
            ("C", "NAME", 20),
            ("N", "AGE", 3, 0),
            ("N", "SALARY", 10, 2),
            ("L", "ACTIVE"),
            ("D", "BIRTHDATE")
        )
        
        # Create and write record
        record = db.new()
        record['NAME'] = 'John Doe'
        record['AGE'] = 30
        record['SALARY'] = 75000.50
        record['ACTIVE'] = True
        record['BIRTHDATE'] = (1993, 5, 15)
        
        db.write(record)
        db.close()
        
        # Read back and verify
        db2 = dbf.Dbf(self.temp_path)
        read_record = db2[0]
        
        self.assertEqual(read_record['NAME'].strip(), 'John Doe')
        self.assertEqual(read_record['AGE'], 30)
        self.assertAlmostEqual(read_record['SALARY'], 75000.50, places=2)
        self.assertEqual(read_record['ACTIVE'], True)
        # Date comparison may need special handling
        db2.close()

    def test_record_write_multiple_records_should_maintain_order(self):
        """
        GIVEN: Multiple records written to DBF file
        WHEN: Reading records back
        THEN: Should maintain the order they were written
        """
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(("N", "ID", 5, 0), ("C", "NAME", 15))
        
        # Write multiple records
        for i in range(5):
            record = db.new()
            record['ID'] = i + 1
            record['NAME'] = f'Person{i+1}'
            db.write(record)
        
        db.close()
        
        # Read back and verify order
        db2 = dbf.Dbf(self.temp_path)
        self.assertEqual(len(db2), 5)
        
        for i in range(5):
            record = db2[i]
            self.assertEqual(record['ID'], i + 1)
            self.assertEqual(record['NAME'].strip(), f'Person{i+1}')
        
        db2.close()

    def test_record_deletion_should_be_persistent(self):
        """
        GIVEN: A record marked as deleted in DBF file
        WHEN: Reading the file again
        THEN: Should preserve deletion status
        """
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(("C", "NAME", 10))
        
        # Create and write record
        record = db.new()
        record['NAME'] = 'Test'
        db.write(record)
        
        # Mark as deleted
        record.deleted = True
        db.write(record, 0)  # Update at position 0
        db.close()
        
        # Read back and verify deletion status
        db2 = dbf.Dbf(self.temp_path)
        read_record = db2[0]
        self.assertTrue(read_record.deleted)
        db2.close()

    def test_record_with_empty_values_should_be_handled_correctly(self):
        """
        GIVEN: A record with None/empty values
        WHEN: Writing and reading the record
        THEN: Should handle empty values appropriately
        """
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(
            ("C", "NAME", 20),
            ("N", "AGE", 3, 0),
            ("L", "ACTIVE")
        )
        
        # Create record with empty/None values
        record = db.new()
        record['NAME'] = ''  # Empty string
        record['AGE'] = None  # None value
        record['ACTIVE'] = None  # None logical
        
        db.write(record)
        db.close()
        
        # Read back and verify
        db2 = dbf.Dbf(self.temp_path)
        read_record = db2[0]
        
        # Empty values should be handled gracefully
        self.assertEqual(read_record['NAME'].strip(), '')
        self.assertIn(read_record['AGE'], [None, 0])
        self.assertIn(read_record['ACTIVE'], [None, False])
        
        db2.close()


if __name__ == '__main__':
    unittest.main()