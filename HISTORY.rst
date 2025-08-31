=======
History
=======

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
