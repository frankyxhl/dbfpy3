#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for dBase III support."""

import unittest
import tempfile
import os
from dbfpy3 import dbf


class TestDBase3Support(unittest.TestCase):
    """Test suite for dBase III file format support."""

    def test_dbase3_signature_support(self):
        """Test that dBase III signature (0x03, 0x83) is supported."""
        with tempfile.NamedTemporaryFile(suffix='.dbf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create a DBF with dBase III signature
            db = dbf.Dbf(tmp_path, new=True)
            db.header.signature = 0x03  # dBase III without memo
            
            # Add fields
            db.add_field(
                ("C", "NAME", 20),
                ("N", "AGE", 3, 0),
                ("D", "BIRTHDATE")
            )
            
            # Add a record
            rec = db.new()
            rec["NAME"] = "John Doe"
            rec["AGE"] = 30
            rec["BIRTHDATE"] = (2000, 1, 1)
            db.write(rec)
            db.close()
            
            # Read it back
            db2 = dbf.Dbf(tmp_path)
            self.assertIn(db2.header.signature, [0x03, 0x83])
            self.assertEqual(len(db2), 1)
            
            record = db2[0]
            self.assertEqual(record["NAME"].strip(), "John Doe")
            self.assertEqual(record["AGE"], 30)
            db2.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_dbase3_with_memo_signature(self):
        """Test dBase III with memo field (0x83)."""
        with tempfile.NamedTemporaryFile(suffix='.dbf', delete=False) as tmp:
            tmp_path = tmp.name
            fpt_path = tmp_path[:-4] + '.fpt'
        
        try:
            # Create a DBF with memo field
            db = dbf.Dbf(tmp_path, new=True)
            
            # Add fields including memo
            db.add_field(
                ("C", "NAME", 20),
                ("M", "NOTES")  # Memo field
            )
            
            # The signature should automatically become 0x83 for dBase III with memo
            # or 0x30 for FoxPro with memo
            rec = db.new()
            rec["NAME"] = "Test User"
            rec["NOTES"] = "This is a test memo field"
            db.write(rec)
            db.close()
            
            # Read it back
            db2 = dbf.Dbf(tmp_path)
            # Should be either 0x83 (dBase III+) or 0x30 (FoxPro)
            self.assertIn(db2.header.signature, [0x30, 0x83])
            self.assertEqual(len(db2), 1)
            
            record = db2[0]
            self.assertEqual(record["NAME"].strip(), "Test User")
            db2.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            if os.path.exists(fpt_path):
                os.unlink(fpt_path)
    
    def test_field_start_position_lenient(self):
        """Test that dBase III files are lenient with field start positions."""
        # This test verifies the fix for the issue where dBase III files
        # have different field alignment than expected
        with tempfile.NamedTemporaryFile(suffix='.dbf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            db = dbf.Dbf(tmp_path, new=True)
            db.header.signature = 0x03
            
            # Add multiple fields to test position calculation
            db.add_field(
                ("C", "FIELD1", 10),
                ("C", "FIELD2", 15),
                ("N", "FIELD3", 5, 0),
                ("D", "FIELD4")
            )
            
            # Verify fields were added correctly
            self.assertEqual(len(db.header.fields), 4)
            
            # Write and close
            rec = db.new()
            rec["FIELD1"] = "Test1"
            rec["FIELD2"] = "Test2"
            rec["FIELD3"] = 123
            rec["FIELD4"] = (2023, 12, 25)
            db.write(rec)
            db.close()
            
            # Read back - this should not raise "fields start does not match" error
            db2 = dbf.Dbf(tmp_path)
            self.assertEqual(len(db2.header.fields), 4)
            self.assertEqual(db2[0]["FIELD1"].strip(), "Test1")
            db2.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()