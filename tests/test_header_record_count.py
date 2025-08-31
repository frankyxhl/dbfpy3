"""Test for header record count update issue fix."""

import unittest
import tempfile
import os
from dbfpy3 import dbf
import datetime


class TestHeaderRecordCount(unittest.TestCase):
    """Test that header record count is properly updated when adding records."""

    def setUp(self):
        """Create a temporary DBF file for testing."""
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix='.dbf')
        os.close(self.temp_fd)

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
        # Also clean up any FPT memo file if created
        fpt_path = self.temp_path.replace('.dbf', '.fpt')
        if os.path.exists(fpt_path):
            os.unlink(fpt_path)

    def test_header_record_count_is_updated_on_append(self):
        """Test that the header record count is properly persisted when appending records."""
        # Create a new DBF file
        with dbf.Dbf(self.temp_path, new=True) as db:
            db.add_field(
                ('C', 'NAME', 30),
                ('D', 'BIRTHDATE'),
                ('N', 'SALARY', 10, 2)
            )
            
            # Add first record
            rec1 = db.new()
            rec1['NAME'] = 'John Doe'
            rec1['BIRTHDATE'] = datetime.date(1990, 1, 15)
            rec1['SALARY'] = 50000.00
            db.write(rec1)
            
            # Check that header shows 1 record
            self.assertEqual(db.header.record_count, 1)
            
            # Add second record
            rec2 = db.new()
            rec2['NAME'] = 'Jane Smith'
            rec2['BIRTHDATE'] = datetime.date(1985, 6, 20)
            rec2['SALARY'] = 60000.00
            db.write(rec2)
            
            # Check that header shows 2 records
            self.assertEqual(db.header.record_count, 2)
            
            # Flush to ensure header is written
            db.flush()
        
        # Re-open the file and verify the record count was persisted
        with dbf.Dbf(self.temp_path) as db:
            # The header should still show 2 records
            self.assertEqual(db.header.record_count, 2)
            
            # Verify we can actually read both records
            records = list(db)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]['NAME'].strip(), 'John Doe')
            self.assertEqual(records[1]['NAME'].strip(), 'Jane Smith')

    def test_header_changed_flag_is_set(self):
        """Test that the header _changed flag is set when adding records."""
        with dbf.Dbf(self.temp_path, new=True) as db:
            db.add_field(('C', 'TEST', 10))
            
            # Initially header should not be marked as changed after field definition
            db.header._changed = False
            
            # Add a record
            rec = db.new()
            rec['TEST'] = 'test'
            db.write(rec)
            
            # Header should now be marked as changed
            self.assertTrue(db.header._changed)

    def test_incremental_append_with_reopening(self):
        """Test appending records across multiple sessions."""
        # First session: create and add one record
        with dbf.Dbf(self.temp_path, new=True) as db:
            db.add_field(('C', 'NAME', 20))
            rec = db.new()
            rec['NAME'] = 'First'
            db.write(rec)
        
        # Second session: append another record
        with dbf.Dbf(self.temp_path) as db:
            self.assertEqual(db.header.record_count, 1)
            rec = db.new()
            rec['NAME'] = 'Second'
            db.write(rec)
            self.assertEqual(db.header.record_count, 2)
        
        # Third session: verify both records are there
        with dbf.Dbf(self.temp_path) as db:
            self.assertEqual(db.header.record_count, 2)
            records = list(db)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]['NAME'].strip(), 'First')
            self.assertEqual(records[1]['NAME'].strip(), 'Second')


if __name__ == '__main__':
    unittest.main()