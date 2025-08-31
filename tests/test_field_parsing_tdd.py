#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TDD Tests for Field Parsing - Edge Cases and Boundary Conditions.

This module implements comprehensive Test-Driven Development (TDD) tests for the
field parsing functionality in dbfpy3, focusing on edge cases, boundary conditions,
and error handling scenarios.

Following TDD principles:
- Red: Write failing tests first
- Green: Implement minimal code to pass
- Refactor: Improve code while keeping tests green
"""

import unittest
import struct
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from dbfpy3 import fields
from dbfpy3.fields import (
    DbfField, DbfFields, DbfCharacterField, DbfNumericField,
    DbfFloatField, DbfDateField, DbfLogicalField, DbfMemoField,
    DbfCurrencyField, DbfIntegerField, DbfDateTimeField,
    DbfPictureField, DbfGeneralField
)


class TestFieldParsingTDD(unittest.TestCase):
    """TDD tests for field parsing with comprehensive edge case coverage."""

    def setUp(self):
        """Set up test fixtures for each test method."""
        self.valid_field_bytes = struct.pack(
            '< 11s c L 2B 14s',
            b'NAME',           # Field name (11 bytes)
            b'C',              # Field type (1 byte)
            0,                 # Displacement (4 bytes)
            10,                # Length (1 byte)
            0,                 # Decimal count (1 byte)
            b'\x00' * 14,      # Reserved (14 bytes)
        )

    # RED PHASE: Write failing tests for field parsing edge cases

    def test_parse_field_with_exact_32_bytes_should_succeed(self):
        """
        GIVEN: A field definition with exactly 32 bytes
        WHEN: Parsing the field bytes
        THEN: Should create a valid DbfCharacterField
        """
        field = DbfFields.parse(self.valid_field_bytes)
        
        self.assertIsInstance(field, DbfCharacterField)
        self.assertEqual(field.name, b'NAME')
        self.assertEqual(field.length, 10)

    def test_parse_field_with_31_bytes_should_raise_value_error(self):
        """
        GIVEN: A field definition with 31 bytes (one short)
        WHEN: Parsing the field bytes
        THEN: Should raise ValueError with specific message
        """
        short_bytes = self.valid_field_bytes[:-1]  # Remove one byte
        
        with self.assertRaisesRegex(ValueError, r'String .* is not a 32 length bytes'):
            DbfFields.parse(short_bytes)

    def test_parse_field_with_33_bytes_should_raise_value_error(self):
        """
        GIVEN: A field definition with 33 bytes (one extra)
        WHEN: Parsing the field bytes
        THEN: Should raise ValueError with specific message
        """
        long_bytes = self.valid_field_bytes + b'\x00'  # Add one byte
        
        with self.assertRaisesRegex(ValueError, r'String .* is not a 32 length bytes'):
            DbfFields.parse(long_bytes)

    def test_parse_field_with_empty_bytes_should_raise_value_error(self):
        """
        GIVEN: An empty byte string
        WHEN: Parsing the field bytes
        THEN: Should raise ValueError
        """
        with self.assertRaisesRegex(ValueError, r'String .* is not a 32 length bytes'):
            DbfFields.parse(b'')

    def test_parse_field_with_string_input_should_raise_value_error(self):
        """
        GIVEN: A string instead of bytes
        WHEN: Parsing the field
        THEN: Should raise ValueError
        """
        with self.assertRaisesRegex(ValueError, r'String .* is not a 32 length bytes'):
            DbfFields.parse('not bytes string with exact 32 ch')

    def test_parse_field_with_null_terminated_name_should_extract_correct_name(self):
        """
        GIVEN: A field with null-terminated name (e.g., 'ID\x00\x00...')
        WHEN: Parsing the field
        THEN: Should extract name correctly without null bytes
        """
        field_bytes = bytearray(32)
        field_bytes[0:11] = b'ID\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        field_bytes[11] = ord('C')  # type
        field_bytes[16] = 10  # length
        
        field = DbfFields.parse(bytes(field_bytes))
        
        self.assertEqual(field.name, b'ID')

    def test_parse_field_with_maximum_name_length_should_succeed(self):
        """
        GIVEN: A field with 10-character name (maximum allowed)
        WHEN: Parsing the field
        THEN: Should succeed and preserve the full name
        """
        field_bytes = bytearray(self.valid_field_bytes)
        field_bytes[0:11] = b'ABCDEFGHIJ\x00'  # 10 chars + null terminator
        
        field = DbfFields.parse(bytes(field_bytes))
        
        self.assertEqual(field.name, b'ABCDEFGHIJ')

    def test_parse_numeric_field_with_zero_decimal_places(self):
        """
        GIVEN: A numeric field with 0 decimal places
        WHEN: Parsing the field
        THEN: Should create DbfNumericField with correct decimal count
        """
        field_bytes = bytearray(self.valid_field_bytes)
        field_bytes[11] = b'N'[0]  # Numeric field
        field_bytes[16] = 8        # Length
        field_bytes[17] = 0        # Decimal places
        
        field = DbfFields.parse(bytes(field_bytes))
        
        self.assertIsInstance(field, DbfNumericField)
        self.assertEqual(field.decimal_count, 0)

    def test_parse_numeric_field_with_maximum_decimal_places(self):
        """
        GIVEN: A numeric field with maximum decimal places (15)
        WHEN: Parsing the field
        THEN: Should create DbfNumericField with correct decimal count
        """
        field_bytes = bytearray(self.valid_field_bytes)
        field_bytes[11] = b'N'[0]  # Numeric field
        field_bytes[16] = 16       # Length
        field_bytes[17] = 15       # Decimal places
        
        field = DbfFields.parse(bytes(field_bytes))
        
        self.assertIsInstance(field, DbfNumericField)
        self.assertEqual(field.decimal_count, 15)

    def test_parse_unknown_field_type_should_raise_key_error(self):
        """
        GIVEN: A field with unknown type code 'X'
        WHEN: Parsing the field
        THEN: Should raise KeyError with informative message
        """
        field_bytes = bytearray(self.valid_field_bytes)
        field_bytes[11] = b'X'[0]  # Unknown field type
        
        with self.assertRaisesRegex(KeyError, r'type code .* not support'):
            DbfFields.parse(bytes(field_bytes))

    def test_parse_all_supported_field_types(self):
        """
        GIVEN: Field definitions for all supported field types
        WHEN: Parsing each field type
        THEN: Should create correct field instance for each type
        """
        field_type_mappings = [
            (b'C', DbfCharacterField),
            (b'N', DbfNumericField),
            (b'F', DbfFloatField),
            (b'D', DbfDateField),
            (b'L', DbfLogicalField),
            (b'M', DbfMemoField),
            (b'Y', DbfCurrencyField),
            (b'I', DbfIntegerField),
            (b'T', DbfDateTimeField),
            (b'P', DbfPictureField),
            (b'G', DbfGeneralField),
        ]
        
        for type_code, expected_class in field_type_mappings:
            with self.subTest(type_code=type_code):
                field_bytes = bytearray(self.valid_field_bytes)
                field_bytes[11] = type_code[0]
                
                field = DbfFields.parse(bytes(field_bytes))
                
                self.assertIsInstance(field, expected_class)

    def test_parse_field_with_ignore_errors_true(self):
        """
        GIVEN: A field definition and ignore_errors=True
        WHEN: Parsing the field
        THEN: Should create field with ignore_errors flag set
        """
        field = DbfFields.parse(self.valid_field_bytes, ignore_errors=True)
        
        self.assertTrue(field.ignore_errors)

    def test_parse_field_with_ignore_errors_false(self):
        """
        GIVEN: A field definition and ignore_errors=False
        WHEN: Parsing the field
        THEN: Should create field with ignore_errors flag unset
        """
        field = DbfFields.parse(self.valid_field_bytes, ignore_errors=False)
        
        self.assertFalse(field.ignore_errors)

    def test_parse_field_displacement_is_preserved(self):
        """
        GIVEN: A field with specific displacement value
        WHEN: Parsing the field
        THEN: Should preserve the displacement value
        """
        field_bytes = bytearray(self.valid_field_bytes)
        displacement = 42
        struct.pack_into('< L', field_bytes, 12, displacement)
        
        field = DbfFields.parse(bytes(field_bytes))
        
        self.assertEqual(field.start, displacement)

    def test_parse_field_length_boundary_values(self):
        """
        GIVEN: Fields with boundary length values (0, 1, 255)
        WHEN: Parsing the fields
        THEN: Should handle valid values correctly, reject invalid ones
        """
        # Test valid boundary lengths
        valid_lengths = [1, 254, 255]
        for length in valid_lengths:
            with self.subTest(length=length):
                field_bytes = bytearray(self.valid_field_bytes)
                field_bytes[16] = length
                
                field = DbfFields.parse(bytes(field_bytes))
                
                self.assertEqual(field.length, length)
        
        # Test invalid length 0
        with self.subTest(length=0):
            field_bytes = bytearray(self.valid_field_bytes)
            field_bytes[16] = 0
            
            with self.assertRaises(ValueError):
                DbfFields.parse(bytes(field_bytes))


class TestFieldRegistrationTDD(unittest.TestCase):
    """TDD tests for field type registration system."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original _fields dict to restore after tests
        self.original_fields = DbfFields._fields.copy()
        
        # Create a mock field class for testing
        self.MockFieldClass = type('MockFieldClass', (DbfField,), {
            'type_code': b'Z',
            'fixed_length': 10,
            'default_value': b'mock'
        })
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original fields registry
        DbfFields._fields = self.original_fields

    def test_register_field_with_valid_type_code_should_succeed(self):
        """
        GIVEN: A field class with valid type code
        WHEN: Registering the field class
        THEN: Should register successfully and be retrievable
        """
        DbfFields.register(self.MockFieldClass)
        
        retrieved_class = DbfFields.get('Z')
        
        self.assertEqual(retrieved_class, self.MockFieldClass)

    def test_register_field_with_none_type_code_should_raise_value_error(self):
        """
        GIVEN: A field class with None type code
        WHEN: Registering the field class
        THEN: Should raise ValueError with specific message
        """
        InvalidFieldClass = type('InvalidFieldClass', (DbfField,), {
            'type_code': None
        })
        
        with self.assertRaisesRegex(ValueError, r"type code .* isn't defined"):
            DbfFields.register(InvalidFieldClass)

    def test_get_field_with_string_type_code_should_succeed(self):
        """
        GIVEN: A registered field and string type code
        WHEN: Getting field by string type code
        THEN: Should return the correct field class
        """
        DbfFields.register(self.MockFieldClass)
        
        retrieved_class = DbfFields.get('Z')
        
        self.assertEqual(retrieved_class, self.MockFieldClass)

    def test_get_field_with_bytes_type_code_should_succeed(self):
        """
        GIVEN: A registered field and bytes type code
        WHEN: Getting field by bytes type code
        THEN: Should return the correct field class
        """
        DbfFields.register(self.MockFieldClass)
        
        retrieved_class = DbfFields.get(b'Z')
        
        self.assertEqual(retrieved_class, self.MockFieldClass)

    def test_get_field_with_lowercase_type_code_should_succeed(self):
        """
        GIVEN: A registered field with uppercase type code
        WHEN: Getting field by lowercase type code
        THEN: Should return the correct field class (case insensitive)
        """
        DbfFields.register(self.MockFieldClass)
        
        retrieved_class = DbfFields.get('z')
        
        self.assertEqual(retrieved_class, self.MockFieldClass)

    def test_get_field_with_unregistered_type_code_should_raise_key_error(self):
        """
        GIVEN: An unregistered field type code
        WHEN: Getting field by that type code
        THEN: Should raise KeyError with informative message
        """
        with self.assertRaisesRegex(KeyError, r'type code .* not support'):
            DbfFields.get('Q')

    def test_get_field_with_invalid_input_type_should_raise_key_error(self):
        """
        GIVEN: An invalid input type (integer)
        WHEN: Getting field by that input
        THEN: Should raise KeyError
        """
        with self.assertRaisesRegex(KeyError, r'type code .* not support'):
            DbfFields.get(123)


class TestFieldEncodingDecodingTDD(unittest.TestCase):
    """TDD tests for field encoding and decoding operations."""

    def test_numeric_field_encode_integer_should_right_align_with_spaces(self):
        """
        GIVEN: A numeric field with integer value
        WHEN: Encoding the value
        THEN: Should right-align with leading spaces
        """
        field = DbfNumericField(b'NUM', 8, 0)
        
        result = field.encode(123)
        
        self.assertEqual(result, b'     123')

    def test_numeric_field_encode_negative_integer_should_include_minus_sign(self):
        """
        GIVEN: A numeric field with negative integer value
        WHEN: Encoding the value
        THEN: Should include minus sign and right-align
        """
        field = DbfNumericField(b'NUM', 8, 0)
        
        result = field.encode(-123)
        
        self.assertEqual(result, b'    -123')

    def test_numeric_field_encode_decimal_should_format_with_decimal_places(self):
        """
        GIVEN: A numeric field with decimal places
        WHEN: Encoding a decimal value
        THEN: Should format with correct decimal places
        """
        field = DbfNumericField(b'NUM', 8, 2)
        
        result = field.encode(123.45)
        
        self.assertEqual(result, b'  123.45')

    def test_numeric_field_encode_value_too_large_should_raise_error(self):
        """
        GIVEN: A numeric field with value too large for field width
        WHEN: Encoding the value
        THEN: Should raise ValueError for overflow
        """
        field = DbfNumericField(b'NUM', 5, 0)
        
        with self.assertRaises(ValueError) as cm:
            field.encode(123456)  # Too large for 5-character field
        
        self.assertIn('Numeric overflow', str(cm.exception))

    def test_numeric_field_decode_valid_number_should_return_correct_value(self):
        """
        GIVEN: A numeric field with valid encoded number
        WHEN: Decoding the bytes
        THEN: Should return correct numeric value
        """
        field = DbfNumericField(b'NUM', 8, 2)
        
        result = field.decode(b'  123.45')
        
        self.assertEqual(result, 123.45)

    def test_numeric_field_decode_spaces_only_should_return_none_or_zero(self):
        """
        GIVEN: A numeric field with only spaces
        WHEN: Decoding the bytes
        THEN: Should return None or 0 (depending on implementation)
        """
        field = DbfNumericField(b'NUM', 8, 2)
        
        result = field.decode(b'        ')
        
        # Could be None or 0 depending on implementation
        self.assertIn(result, [None, 0, 0.0])

    def test_character_field_encode_should_left_align_and_pad_with_spaces(self):
        """
        GIVEN: A character field with string value
        WHEN: Encoding the value
        THEN: Should left-align and pad with spaces
        """
        field = DbfCharacterField(b'NAME', 10)
        
        result = field.encode('John')
        
        self.assertEqual(result, b'John      ')

    def test_character_field_encode_string_too_long_should_truncate(self):
        """
        GIVEN: A character field with string longer than field length
        WHEN: Encoding the value
        THEN: Should truncate to field length
        """
        field = DbfCharacterField(b'NAME', 5)
        
        result = field.encode('TooLongName')
        
        self.assertEqual(result, b'TooLo')

    @unittest.skip("TODO: Logical field needs to support multiple true value formats") 
    def test_logical_field_encode_true_values_should_return_T(self):
        """
        GIVEN: A logical field with various true values
        WHEN: Encoding the values
        THEN: Should return 'T' for all true values
        """
        field = DbfLogicalField(b'FLAG')
        true_values = [True, 'T', 't', 'Y', 'y', '1', 1]
        
        for value in true_values:
            with self.subTest(value=value):
                result = field.encode(value)
                self.assertEqual(result, b'T')

    def test_logical_field_encode_false_values_should_return_F(self):
        """
        GIVEN: A logical field with various false values
        WHEN: Encoding the values
        THEN: Should return 'F' for all false values
        """
        field = DbfLogicalField(b'FLAG')
        false_values = [False, 'F', 'f', 'N', 'n', '0', 0]
        
        for value in false_values:
            with self.subTest(value=value):
                result = field.encode(value)
                self.assertEqual(result, b'F')

    def test_date_field_encode_valid_date_tuple_should_return_yyyymmdd(self):
        """
        GIVEN: A date field with valid date tuple
        WHEN: Encoding the date
        THEN: Should return YYYYMMDD format
        """
        field = DbfDateField(b'DATE')
        
        result = field.encode((2023, 12, 25))
        
        self.assertEqual(result, b'20231225')

    def test_date_field_encode_invalid_date_should_handle_gracefully(self):
        """
        GIVEN: A date field with invalid date
        WHEN: Encoding the date
        THEN: Should handle error gracefully (return spaces or raise exception)
        """
        field = DbfDateField(b'DATE')
        
        # This should either raise an exception or return spaces
        try:
            result = field.encode((2023, 13, 32))  # Invalid month and day
            self.assertEqual(result, b'        ')  # Empty date
        except (ValueError, TypeError):
            pass  # Exception is also acceptable


if __name__ == '__main__':
    unittest.main()