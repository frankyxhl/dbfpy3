"""
Unit tests for FoxPro Double field (type B) support
"""

import unittest
import tempfile
import os
import struct
import math
from dbfpy3 import dbf
from dbfpy3.fields import DbfDoubleField, DbfFields


class TestDbfDoubleField(unittest.TestCase):
    """Test cases for FoxPro Double field support."""

    def setUp(self):
        """Set up test fixtures."""
        self.field = DbfDoubleField(b'DOUBLE_VAL', length=8)

    def test_field_properties(self):
        """Test basic field properties."""
        self.assertEqual(self.field.type_code, b'B')
        self.assertEqual(self.field.fixed_length, 8)
        self.assertEqual(self.field.default_value, 0.0)
        self.assertEqual(self.field.name, b'DOUBLE_VAL')

    def test_encode_decode_basic_values(self):
        """Test encoding and decoding of basic double values."""
        test_values = [
            0.0,
            1.0,
            -1.0,
            3.14159265359,
            1e-10,
            1e10,
            math.pi,
            math.e,
            123.456789,
            -999.999999,
        ]

        for value in test_values:
            with self.subTest(value=value):
                encoded = self.field.encode(value)
                decoded = self.field.decode(encoded)
                
                # Check encoded length
                self.assertEqual(len(encoded), 8)
                
                # Check precision (IEEE 754 double precision)
                self.assertAlmostEqual(decoded, value, places=15)

    def test_encode_none_value(self):
        """Test encoding None value."""
        encoded = self.field.encode(None)
        self.assertEqual(encoded, b'\x00' * 8)
        
        decoded = self.field.decode(encoded)
        self.assertEqual(decoded, 0.0)

    def test_decode_zero_bytes(self):
        """Test decoding zero bytes."""
        zero_bytes = b'\x00' * 8
        decoded = self.field.decode(zero_bytes)
        self.assertEqual(decoded, 0.0)

    def test_encode_decode_edge_cases(self):
        """Test encoding and decoding edge cases."""
        # Very small numbers
        small_value = 1e-300
        encoded = self.field.encode(small_value)
        decoded = self.field.decode(encoded)
        self.assertAlmostEqual(decoded, small_value, places=15)
        
        # Very large numbers
        large_value = 1e300
        encoded = self.field.encode(large_value)
        decoded = self.field.decode(encoded)
        self.assertAlmostEqual(decoded, large_value, places=15)

    def test_struct_format_compatibility(self):
        """Test compatibility with Python's struct module."""
        test_value = 3.141592653589793
        
        # Our encoding should match struct.pack
        our_encoded = self.field.encode(test_value)
        struct_encoded = struct.pack("<d", test_value)
        
        self.assertEqual(our_encoded, struct_encoded)
        
        # Our decoding should match struct.unpack
        our_decoded = self.field.decode(struct_encoded)
        struct_decoded = struct.unpack("<d", struct_encoded)[0]
        
        self.assertEqual(our_decoded, struct_decoded)

    def test_field_registration(self):
        """Test that Double field is properly registered."""
        field_class = DbfFields.get('B')
        self.assertEqual(field_class, DbfDoubleField)
        
        field_class = DbfFields.get(b'B')
        self.assertEqual(field_class, DbfDoubleField)

    def test_dbf_integration(self):
        """Test Double field integration with DBF files."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Create DBF with Double fields
            db = dbf.Dbf(temp_path, new=True)
            db.add_field(
                ('C', 'NAME', 20),
                ('B', 'LATITUDE', 8),
                ('B', 'LONGITUDE', 8),
                ('B', 'ALTITUDE', 8),
            )
            
            # Test data with high precision
            test_records = [
                {
                    'NAME': 'GPS Point 1',
                    'LATITUDE': 40.748817,
                    'LONGITUDE': -73.985428,
                    'ALTITUDE': 10.5,
                },
                {
                    'NAME': 'GPS Point 2',
                    'LATITUDE': -33.867487,
                    'LONGITUDE': 151.206990,
                    'ALTITUDE': 58.0,
                },
                {
                    'NAME': 'High Precision',
                    'LATITUDE': 40.74881700123456,
                    'LONGITUDE': -73.98542800987654,
                    'ALTITUDE': 10.50000000000001,
                },
            ]
            
            # Write records
            for data in test_records:
                rec = db.new()
                for field_name, value in data.items():
                    rec[field_name] = value
                db.write(rec)
            
            db.close()
            
            # Read back and verify
            db2 = dbf.Dbf(temp_path)
            self.assertEqual(len(db2), 3)
            
            for i, record in enumerate(db2):
                original = test_records[i]
                
                # Check name field
                self.assertEqual(record['NAME'].strip(), original['NAME'])
                
                # Check double fields with high precision
                self.assertAlmostEqual(record['LATITUDE'], original['LATITUDE'], places=14)
                self.assertAlmostEqual(record['LONGITUDE'], original['LONGITUDE'], places=14)
                self.assertAlmostEqual(record['ALTITUDE'], original['ALTITUDE'], places=14)
            
            db2.close()
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_field_creation_from_tuple(self):
        """Test creating Double field from field definition tuple."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            db = dbf.Dbf(temp_path, new=True)
            
            # Add Double field using tuple notation
            db.add_field(('B', 'DISTANCE', 8))
            
            # Verify field was created correctly
            field = db.header.fields[0]
            self.assertEqual(field.type_code, b'B')
            self.assertEqual(field.name, b'DISTANCE')
            self.assertEqual(field.length, 8)
            
            # Test writing and reading
            rec = db.new()
            rec['DISTANCE'] = 42.123456789
            db.write(rec)
            db.close()
            
            # Verify data
            db2 = dbf.Dbf(temp_path)
            record = db2[0]
            self.assertAlmostEqual(record['DISTANCE'], 42.123456789, places=14)
            db2.close()
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()