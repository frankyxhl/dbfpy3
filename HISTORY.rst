=======
History
=======

5.0.0 (2025-08-31) - PANDAS INTEGRATION
----------------------------------------

* **Major Feature**: Complete pandas DataFrame integration
* Added ``dbfpy3.pandas_integration`` module with bidirectional conversion
* Intelligent type mapping between pandas dtypes and DBF field types
* Memory-efficient chunked processing for large files (default 10,000 records)
* Optional pandas dependency - core library remains zero-dependency
* Added ``read_dbf()`` and ``write_dbf()`` convenience functions
* Added ``DbfPandasConverter`` class for advanced use cases
* Comprehensive test suite - 17 new TDD tests (217 total, 100% passing)
* Added 4 BDD feature scenarios for real-world use cases
* Full documentation and migration guide included
* Backward compatible - no breaking changes to existing API

4.2.4 (2025-08-31) - CRITICAL FIX
----------------------------------

* **CRITICAL**: Fixed data integrity bug where header record count wasn't persisting to disk
* Bug caused new records to be lost when files were reopened
* Root cause: header._changed flag wasn't set when incrementing record_count
* Added comprehensive test coverage for header persistence
* All users should upgrade immediately to prevent data loss

4.2.3 (Previous)
----------------

* Added FoxPro Double field type B support (IEEE 754 double-precision)
* Enhanced test suite to 200 tests
* Improved documentation

0.1.0 (2020-12-26)
------------------

* First release on PyPI.
