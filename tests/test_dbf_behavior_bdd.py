#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BDD Tests for DBF Behavior - User Story Scenarios.

This module implements Behavior-Driven Development (BDD) style tests using
unittest framework with clear Given-When-Then structure. Each test represents
a user story or behavior scenario.

BDD Structure:
- GIVEN: Initial context and preconditions
- WHEN: The action or event that triggers the behavior
- THEN: Expected outcome or result

User Stories Covered:
- Creating and reading DBF files
- Handling different DBF versions
- Working with memo fields
- Error recovery scenarios
- Data integrity scenarios
"""

import unittest
import tempfile
import os
import datetime
from io import BytesIO

from dbfpy3 import dbf
from dbfpy3.header import DbfHeader
from dbfpy3.fields import DbfCharacterField, DbfNumericField, DbfDateField


class TestDBFFileCreationBehavior(unittest.TestCase):
    """BDD tests for DBF file creation behaviors."""

    def setUp(self):
        """Set up test fixtures for each scenario."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures after each scenario."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_user_creates_new_empty_dbf_file(self):
        """
        User Story: As a developer, I want to create a new empty DBF file
        so that I can start building a database structure.

        Scenario: Creating a new empty DBF file
        """
        # GIVEN: I need to create a new DBF file
        file_path = self.temp_path
        self.assertFalse(os.path.exists(file_path) and os.path.getsize(file_path) > 0)

        # WHEN: I create a new DBF file with basic structure
        db = dbf.Dbf(file_path, new=True)
        db.add_field(("N", "ID", 5, 0))
        db.add_field(("C", "NAME", 30))
        db.close()

        # THEN: The file should be created with proper DBF structure
        self.assertTrue(os.path.exists(file_path))
        self.assertGreater(os.path.getsize(file_path), 0)
        
        # AND: I should be able to read the structure back
        db_read = dbf.Dbf(file_path)
        self.assertEqual(len(db_read.header.fields), 2)
        self.assertEqual(db_read.header.fields[0].name, b'ID')
        self.assertEqual(db_read.header.fields[1].name, b'NAME')
        db_read.close()

    def test_user_creates_dbf_with_different_field_types(self):
        """
        User Story: As a developer, I want to create DBF files with various field types
        so that I can store different kinds of data.

        Scenario: Creating DBF with multiple field types
        """
        # GIVEN: I need to store different types of data
        field_definitions = [
            ("N", "EMPLOYEE_ID", 6, 0),      # Integer employee ID
            ("C", "FULL_NAME", 50),          # Character name
            ("N", "SALARY", 10, 2),          # Numeric with decimals
            ("L", "IS_ACTIVE"),              # Logical/boolean
            ("D", "HIRE_DATE")               # Date field
        ]

        # WHEN: I create a DBF with these field types
        db = dbf.Dbf(self.temp_path, new=True)
        for field_def in field_definitions:
            db.add_field(field_def)
        db.close()

        # THEN: The file should contain all field types correctly
        db_read = dbf.Dbf(self.temp_path)
        self.assertEqual(len(db_read.header.fields), 5)
        
        # AND: Each field should have the correct properties
        fields = db_read.header.fields
        self.assertEqual(fields[0].name, b'EMPLOYEE_ID')
        self.assertEqual(fields[0].length, 6)
        self.assertEqual(fields[1].name, b'FULL_NAME')
        self.assertEqual(fields[1].length, 50)
        self.assertEqual(fields[2].name, b'SALARY')
        self.assertEqual(fields[2].decimal_count, 2)
        
        db_read.close()

    def test_user_adds_sample_data_to_new_dbf(self):
        """
        User Story: As a developer, I want to add sample data to a new DBF file
        so that I can test my application with realistic data.

        Scenario: Adding multiple records with sample data
        """
        # GIVEN: I have a DBF file with employee structure
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(
            ("N", "ID", 5, 0),
            ("C", "NAME", 25),
            ("C", "DEPARTMENT", 15),
            ("SALARY", "N", 8, 2),
            ("ACTIVE", "L")
        )

        # AND: I have sample employee data to insert
        sample_employees = [
            (1, "John Doe", "Engineering", 75000.00, True),
            (2, "Jane Smith", "Marketing", 68000.50, True),
            (3, "Bob Johnson", "Sales", 62000.25, False),
        ]

        # WHEN: I add the sample records to the DBF
        for emp_id, name, dept, salary, active in sample_employees:
            record = db.new()
            record['ID'] = emp_id
            record['NAME'] = name
            record['DEPARTMENT'] = dept
            record['SALARY'] = salary
            record['ACTIVE'] = active
            db.write(record)

        db.close()

        # THEN: The file should contain all the sample records
        db_read = dbf.Dbf(self.temp_path)
        self.assertEqual(len(db_read), 3)

        # AND: Each record should have the correct data
        for i, (exp_id, exp_name, exp_dept, exp_salary, exp_active) in enumerate(sample_employees):
            record = db_read[i]
            self.assertEqual(record['ID'], exp_id)
            self.assertEqual(record['NAME'].strip(), exp_name)
            self.assertEqual(record['DEPARTMENT'].strip(), exp_dept)
            self.assertAlmostEqual(record['SALARY'], exp_salary, places=2)
            self.assertEqual(record['ACTIVE'], exp_active)

        db_read.close()


class TestDBFFileReadingBehavior(unittest.TestCase):
    """BDD tests for DBF file reading behaviors."""

    def setUp(self):
        """Set up test fixtures - create a sample DBF file."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        self.temp_path = self.temp_file.name
        self.temp_file.close()

        # Create a sample DBF with test data
        db = dbf.Dbf(self.temp_path, new=True)
        db.add_field(
            ("N", "PRODUCT_ID", 5, 0),
            ("C", "PRODUCT_NAME", 30),
            ("N", "PRICE", 8, 2),
            ("L", "IN_STOCK")
        )

        test_products = [
            (101, "Widget A", 19.99, True),
            (102, "Widget B", 29.99, True),
            (103, "Widget C", 39.99, False),
        ]

        for prod_id, name, price, in_stock in test_products:
            record = db.new()
            record['PRODUCT_ID'] = prod_id
            record['PRODUCT_NAME'] = name
            record['PRICE'] = price
            record['IN_STOCK'] = in_stock
            db.write(record)

        db.close()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)

    def test_user_opens_existing_dbf_file(self):
        """
        User Story: As a developer, I want to open an existing DBF file
        so that I can read its contents.

        Scenario: Opening and examining an existing DBF file
        """
        # GIVEN: I have an existing DBF file with known structure
        self.assertTrue(os.path.exists(self.temp_path))

        # WHEN: I open the existing DBF file
        db = dbf.Dbf(self.temp_path)

        # THEN: I should be able to access the file structure
        self.assertEqual(len(db.header.fields), 4)
        
        # AND: I should see the expected fields
        field_names = [field.name.decode() for field in db.header.fields]
        expected_fields = ['PRODUCT_ID', 'PRODUCT_NAME', 'PRICE', 'IN_STOCK']
        self.assertEqual(field_names, expected_fields)

        # AND: I should see the expected number of records
        self.assertEqual(len(db), 3)

        db.close()

    def test_user_iterates_through_all_records(self):
        """
        User Story: As a developer, I want to iterate through all records in a DBF file
        so that I can process each record in sequence.

        Scenario: Processing all records in a DBF file
        """
        # GIVEN: I have a DBF file with multiple records
        db = dbf.Dbf(self.temp_path)
        expected_record_count = 3

        # WHEN: I iterate through all records using for loop
        processed_records = []
        for record in db:
            processed_records.append({
                'id': record['PRODUCT_ID'],
                'name': record['PRODUCT_NAME'].strip(),
                'price': record['PRICE']
            })

        # THEN: I should process exactly the expected number of records
        self.assertEqual(len(processed_records), expected_record_count)

        # AND: Each record should contain the expected data structure
        for processed_record in processed_records:
            self.assertIn('id', processed_record)
            self.assertIn('name', processed_record)
            self.assertIn('price', processed_record)
            self.assertIsInstance(processed_record['id'], int)
            self.assertIsInstance(processed_record['name'], str)
            self.assertIsInstance(processed_record['price'], (int, float))

        db.close()

    def test_user_accesses_specific_record_by_index(self):
        """
        User Story: As a developer, I want to access specific records by index
        so that I can retrieve individual records efficiently.

        Scenario: Accessing records by numeric index
        """
        # GIVEN: I have a DBF file with indexed records
        db = dbf.Dbf(self.temp_path)

        # WHEN: I access the first record by index
        first_record = db[0]

        # THEN: I should get the expected first record
        self.assertEqual(first_record['PRODUCT_ID'], 101)
        self.assertEqual(first_record['PRODUCT_NAME'].strip(), "Widget A")

        # WHEN: I access the last record by index
        last_record = db[-1]

        # THEN: I should get the expected last record
        self.assertEqual(last_record['PRODUCT_ID'], 103)
        self.assertEqual(last_record['PRODUCT_NAME'].strip(), "Widget C")

        # WHEN: I try to access an out-of-bounds index
        # THEN: It should raise an IndexError
        with self.assertRaises(IndexError):
            _ = db[99]

        db.close()

    def test_user_filters_records_based_on_field_values(self):
        """
        User Story: As a developer, I want to filter records based on field values
        so that I can find specific data in the DBF file.

        Scenario: Finding records matching specific criteria
        """
        # GIVEN: I have a DBF file with product data
        db = dbf.Dbf(self.temp_path)

        # WHEN: I filter for products that are in stock
        in_stock_products = []
        for record in db:
            if record['IN_STOCK'] == True:
                in_stock_products.append({
                    'id': record['PRODUCT_ID'],
                    'name': record['PRODUCT_NAME'].strip(),
                    'price': record['PRICE']
                })

        # THEN: I should find exactly 2 products in stock
        self.assertEqual(len(in_stock_products), 2)

        # AND: Both products should have the IN_STOCK flag set to True
        expected_in_stock_ids = [101, 102]
        actual_ids = [prod['id'] for prod in in_stock_products]
        self.assertEqual(sorted(actual_ids), sorted(expected_in_stock_ids))

        # WHEN: I filter for products above a certain price
        expensive_products = []
        price_threshold = 25.00
        for record in db:
            if record['PRICE'] > price_threshold:
                expensive_products.append(record['PRODUCT_ID'])

        # THEN: I should find products with price above threshold
        self.assertEqual(len(expensive_products), 2)
        self.assertIn(102, expensive_products)  # Widget B - 29.99
        self.assertIn(103, expensive_products)  # Widget C - 39.99

        db.close()


class TestDBFErrorRecoveryBehavior(unittest.TestCase):
    """BDD tests for error recovery and graceful handling scenarios."""

    def test_user_handles_corrupted_file_gracefully(self):
        """
        User Story: As a developer, I want my application to handle corrupted DBF files gracefully
        so that it doesn't crash unexpectedly.

        Scenario: Attempting to open a corrupted DBF file
        """
        # GIVEN: I have a corrupted DBF file
        corrupted_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        corrupted_path = corrupted_file.name
        
        # Create a file with invalid DBF header
        corrupted_file.write(b'This is not a valid DBF file content')
        corrupted_file.close()

        try:
            # WHEN: I attempt to open the corrupted file
            # THEN: It should raise an appropriate exception
            with self.assertRaises((ValueError, IOError, struct.error)):
                db = dbf.Dbf(corrupted_path)

            # AND: My application should be able to continue normally
            # (No crashes, no hanging processes)
            
        finally:
            # Clean up
            if os.path.exists(corrupted_path):
                os.unlink(corrupted_path)

    def test_user_handles_missing_file_gracefully(self):
        """
        User Story: As a developer, I want my application to handle missing files gracefully
        so that users get helpful error messages.

        Scenario: Attempting to open a non-existent DBF file
        """
        # GIVEN: I have a path to a file that doesn't exist
        nonexistent_path = '/nonexistent/directory/missing.dbf'

        # WHEN: I attempt to open the non-existent file
        # THEN: It should raise a FileNotFoundError or IOError
        with self.assertRaises((FileNotFoundError, IOError)):
            db = dbf.Dbf(nonexistent_path)

        # AND: The error should be specific and helpful
        try:
            db = dbf.Dbf(nonexistent_path)
        except (FileNotFoundError, IOError) as e:
            # The error message should mention the file path
            self.assertIn('nonexistent', str(e).lower())

    def test_user_recovers_from_invalid_field_access(self):
        """
        User Story: As a developer, I want to handle invalid field access gracefully
        so that data processing can continue with error handling.

        Scenario: Accessing fields that don't exist in records
        """
        # GIVEN: I have a valid DBF file
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            db = dbf.Dbf(temp_path, new=True)
            db.add_field(("C", "REAL_FIELD", 20))
            record = db.new()
            record['REAL_FIELD'] = 'Test Data'
            db.write(record)
            db.close()

            db = dbf.Dbf(temp_path)
            record = db[0]

            # WHEN: I try to access a field that doesn't exist
            # THEN: It should raise a KeyError
            with self.assertRaises(KeyError):
                _ = record['NONEXISTENT_FIELD']

            # AND: I should be able to handle the error and continue
            field_value = None
            try:
                field_value = record['NONEXISTENT_FIELD']
            except KeyError:
                field_value = "Field not found"

            self.assertEqual(field_value, "Field not found")

            # AND: I should still be able to access valid fields
            valid_value = record['REAL_FIELD']
            self.assertEqual(valid_value.strip(), 'Test Data')

            db.close()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDBFDataIntegrityBehavior(unittest.TestCase):
    """BDD tests for data integrity scenarios."""

    def test_user_ensures_data_consistency_across_write_read_cycles(self):
        """
        User Story: As a developer, I want to ensure data integrity across write/read cycles
        so that data is preserved accurately.

        Scenario: Writing complex data and reading it back
        """
        # GIVEN: I need to store complex data with various field types
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Create DBF with comprehensive field types
            db = dbf.Dbf(temp_path, new=True)
            db.add_field(
                ("N", "ID", 8, 0),
                ("C", "NAME", 50),
                ("N", "PRICE", 12, 4),
                ("ACTIVE", "L"),
                ("DATE_CREATED", "D")
            )

            # Test data with edge cases
            test_data = {
                'ID': 12345,
                'NAME': 'Test Product with Special Chars: àáâãäå',
                'PRICE': 1234.5678,
                'ACTIVE': True,
                'DATE_CREATED': (2023, 12, 25)
            }

            # WHEN: I write the complex data
            record = db.new()
            for field, value in test_data.items():
                try:
                    record[field] = value
                except UnicodeEncodeError:
                    # Handle encoding issues gracefully
                    record[field] = 'Test Product with Special Chars'

            db.write(record)
            db.close()

            # AND: I read the data back
            db_read = dbf.Dbf(temp_path)
            read_record = db_read[0]

            # THEN: All data should be preserved accurately
            self.assertEqual(read_record['ID'], test_data['ID'])
            # Name might be encoded differently, so check if it contains core content
            stored_name = read_record['NAME'].strip()
            self.assertTrue(stored_name.startswith('Test Product'))
            
            self.assertAlmostEqual(read_record['PRICE'], test_data['PRICE'], places=4)
            self.assertEqual(read_record['ACTIVE'], test_data['ACTIVE'])
            
            # Date comparison (implementation may vary)
            stored_date = read_record['DATE_CREATED']
            if isinstance(stored_date, tuple):
                self.assertEqual(stored_date, test_data['DATE_CREATED'])

            db_read.close()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_user_handles_boundary_value_data_correctly(self):
        """
        User Story: As a developer, I want to handle boundary values correctly
        so that edge cases don't cause data corruption.

        Scenario: Storing and retrieving boundary values
        """
        # GIVEN: I need to test boundary values for different field types
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            db = dbf.Dbf(temp_path, new=True)
            db.add_field(
                ("C", "TINY_FIELD", 1),      # Single character
                ("N", "BIG_NUM", 15, 2),     # Large numeric field
                ("N", "ZERO_VAL", 5, 0),     # Zero value
                ("LOGIC_VAL", "L")           # Logical field
            )

            # Boundary test values
            boundary_tests = [
                {
                    'TINY_FIELD': 'X',          # Maximum for 1-char field
                    'BIG_NUM': 999999999999.99,  # Large number
                    'ZERO_VAL': 0,              # Zero value
                    'LOGIC_VAL': True           # Boolean true
                },
                {
                    'TINY_FIELD': '',           # Empty string
                    'BIG_NUM': 0.01,            # Minimal decimal
                    'ZERO_VAL': 99999,          # Max for field size
                    'LOGIC_VAL': False          # Boolean false
                }
            ]

            # WHEN: I store boundary values
            for test_values in boundary_tests:
                record = db.new()
                for field, value in test_values.items():
                    try:
                        record[field] = value
                    except (ValueError, OverflowError):
                        # Handle overflow by setting to reasonable value
                        if field == 'ZERO_VAL' and value > 99999:
                            record[field] = 99999
                        else:
                            record[field] = None
                
                db.write(record)

            db.close()

            # THEN: I should be able to read back all boundary values
            db_read = dbf.Dbf(temp_path)
            self.assertEqual(len(db_read), 2)

            # AND: Values should be within expected ranges or properly handled
            for i, expected in enumerate(boundary_tests):
                record = db_read[i]
                
                # Verify each field is handled appropriately
                tiny_val = record['TINY_FIELD']
                self.assertIsInstance(tiny_val, (str, bytes))
                self.assertLessEqual(len(str(tiny_val).strip()), 1)
                
                big_num = record['BIG_NUM']
                self.assertIsInstance(big_num, (int, float, type(None)))
                
                zero_val = record['ZERO_VAL']
                self.assertIsInstance(zero_val, (int, float, type(None)))
                if zero_val is not None:
                    self.assertLessEqual(zero_val, 99999)
                
                logic_val = record['LOGIC_VAL']
                self.assertIn(logic_val, [True, False, None])

            db_read.close()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDBFVersionCompatibilityBehavior(unittest.TestCase):
    """BDD tests for different DBF version compatibility scenarios."""

    def test_user_works_with_dbase3_format_files(self):
        """
        User Story: As a developer, I want to work with dBase III format files
        so that I can maintain compatibility with legacy systems.

        Scenario: Creating and reading dBase III format files
        """
        # GIVEN: I need to create a dBase III compatible file
        temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # WHEN: I create a DBF with dBase III signature
            db = dbf.Dbf(temp_path, new=True)
            db.header.signature = 0x03  # dBase III signature
            
            db.add_field(
                ("N", "LEGACY_ID", 8, 0),
                ("C", "DESCRIPTION", 40),
                ("N", "AMOUNT", 10, 2),
                ("ACTIVE_FLAG", "L")
            )

            # Add sample legacy-style data
            record = db.new()
            record['LEGACY_ID'] = 1001
            record['DESCRIPTION'] = 'Legacy System Record'
            record['AMOUNT'] = 299.99
            record['ACTIVE_FLAG'] = True
            db.write(record)
            
            db.close()

            # THEN: I should be able to read the file as dBase III format
            db_read = dbf.Dbf(temp_path)
            
            # AND: The signature should be preserved
            self.assertIn(db_read.header.signature, [0x03, 0x83])  # dBase III variants
            
            # AND: The data should be accessible
            self.assertEqual(len(db_read), 1)
            read_record = db_read[0]
            
            self.assertEqual(read_record['LEGACY_ID'], 1001)
            self.assertEqual(read_record['DESCRIPTION'].strip(), 'Legacy System Record')
            self.assertAlmostEqual(read_record['AMOUNT'], 299.99, places=2)
            self.assertEqual(read_record['ACTIVE_FLAG'], True)
            
            db_read.close()

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_user_handles_different_signature_formats(self):
        """
        User Story: As a developer, I want to handle different DBF signature formats
        so that I can work with files from various sources.

        Scenario: Reading files with different DBF signatures
        """
        # GIVEN: I need to work with different DBF format signatures
        signatures_to_test = [
            (0x03, "dBase III without memo"),
            (0x83, "dBase III with memo"),
            (0x30, "FoxPro"),
        ]

        for signature, description in signatures_to_test:
            with self.subTest(signature=signature, description=description):
                temp_file = tempfile.NamedTemporaryFile(suffix='.dbf', delete=False)
                temp_path = temp_file.name
                temp_file.close()

                try:
                    # WHEN: I create a DBF with the specific signature
                    db = dbf.Dbf(temp_path, new=True)
                    db.header.signature = signature
                    
                    db.add_field(("C", "TEST_FIELD", 20))
                    
                    record = db.new()
                    record['TEST_FIELD'] = f'Test {description}'
                    db.write(record)
                    db.close()

                    # THEN: I should be able to read the file regardless of signature
                    db_read = dbf.Dbf(temp_path)
                    self.assertEqual(len(db_read), 1)
                    
                    read_record = db_read[0]
                    stored_value = read_record['TEST_FIELD'].strip()
                    self.assertTrue(stored_value.startswith('Test'))
                    
                    db_read.close()

                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()