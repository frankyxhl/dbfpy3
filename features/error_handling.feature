# language: en
@error-handling @robustness
Feature: Error Handling and Recovery
  As a developer building robust applications
  I want the dbfpy3 library to handle errors gracefully
  So that my applications can recover from unexpected situations and provide meaningful feedback

  Background:
    Given I am testing error handling capabilities
    And I have access to the dbfpy3 library

  @critical @file-errors
  Scenario: Handle missing DBF file gracefully
    Given I have a path to a non-existent DBF file "/path/to/missing.dbf"
    When I attempt to open the missing file
    Then I should receive a FileNotFoundError
    And the error message should indicate the file cannot be found
    And the error message should include the attempted file path
    And my application should continue running normally

  @critical @file-errors
  Scenario: Handle corrupted DBF file header
    Given I have a file with corrupted DBF header content
    When I attempt to open the corrupted file
    Then I should receive an appropriate parsing error
    And the error should indicate header corruption
    And the system should not crash or hang
    And I should be able to handle the error programmatically

  @file-errors
  Scenario: Handle truncated DBF files
    Given I have a DBF file that was truncated during writing
    When I attempt to read beyond the available data
    Then I should receive an end-of-file error
    And the error should indicate insufficient data
    And I should be able to read the available portion of the file

  @permission-errors
  Scenario: Handle file permission issues
    Given I have a DBF file with read-only permissions
    When I attempt to open the file for writing
    Then I should receive a permission error
    And the error should indicate access is denied
    When I have insufficient permissions to create a new file
    Then I should receive an appropriate permission error

  @field-validation
  Scenario: Validate field definitions during creation
    Given I am creating a new DBF file
    When I try to add a field with invalid name characters
    Then I should receive a field validation error
    When I try to add a field with a name exceeding 10 characters
    Then I should receive a field name length error
    When I try to add a field with invalid field type
    Then I should receive a field type validation error

  @data-validation
  Scenario: Handle invalid data types in records
    Given I have a DBF file with numeric field definitions
    When I try to store non-numeric data in a numeric field
    Then I should receive a data type validation error
    When I try to store a string longer than the field length
    Then the data should be truncated appropriately
    And I should receive a warning about truncation

  @boundary-conditions
  Scenario: Handle boundary value conditions
    Given I have a DBF file with specific field sizes
    When I store the maximum allowed value for a numeric field
    Then the value should be stored successfully
    When I try to store a value exceeding the field capacity
    Then I should receive an overflow error
    And the error should indicate the value is too large

  @index-errors
  Scenario: Handle invalid record access attempts
    Given I have a DBF file with 10 records
    When I try to access record index 15
    Then I should receive an IndexError
    When I try to access record index -15
    Then I should receive an IndexError
    And the error should indicate the index is out of bounds

  @field-access-errors
  Scenario: Handle invalid field access in records
    Given I have a record from a DBF file
    When I try to access a field that doesn't exist
    Then I should receive a KeyError
    And the error should indicate the field name is not found
    When I try to access fields using invalid data types as keys
    Then I should receive an appropriate type error

  @memory-errors
  Scenario: Handle memory limitations gracefully
    Given I am working with very large DBF files
    When the system runs low on available memory
    Then the operations should degrade gracefully
    And I should receive memory-related error messages
    And the system should not become unresponsive

  @concurrent-access
  Scenario: Handle concurrent file access conflicts
    Given I have a DBF file that might be accessed concurrently
    When another process is writing to the same file
    Then I should receive a file locking error
    And the error should indicate the file is in use
    When I try to write while another process is reading
    Then appropriate file sharing errors should be reported

  @encoding-errors
  Scenario: Handle character encoding issues
    Given I have a DBF file with specific character encoding
    When I try to store characters not supported by the encoding
    Then I should receive an encoding error
    And the error should indicate which characters cannot be encoded
    When I encounter unknown encoding in an existing file
    Then I should receive a decoding error with helpful information

  @format-errors
  Scenario: Handle unsupported DBF format versions
    Given I have a DBF file with an unsupported format version
    When I attempt to open the unsupported file
    Then I should receive a format not supported error
    And the error should indicate the unsupported version number
    When I encounter unknown field types in a file
    Then I should receive appropriate field type errors

  @recovery-scenarios
  Scenario: Provide recovery options for common errors
    Given I encounter a partially corrupted DBF file
    When the header is readable but some records are corrupted
    Then I should be able to read the valid records
    And I should receive warnings about corrupted records
    And I should be able to skip corrupted records and continue

  @error-context
  Scenario: Provide detailed error context information
    Given any error occurs during DBF operations
    When I examine the error information
    Then I should see the specific operation that failed
    And I should see the file path involved in the error
    And I should see the record number if applicable
    And I should see the field name if applicable

  @cascading-errors
  Scenario: Handle cascading error conditions
    Given I have multiple dependent operations
    When the first operation fails
    Then subsequent operations should handle the failure state
    And I should not receive confusing secondary errors
    When I try to perform operations on a closed file
    Then I should receive clear "file not open" errors

  @cleanup-after-errors
  Scenario: Ensure proper cleanup after errors occur
    Given I have file handles open during operations
    When an error occurs during processing
    Then file handles should be properly closed
    And temporary resources should be cleaned up
    And the system should be in a consistent state for recovery

  @error-logging
  Scenario: Support error logging and debugging
    Given I have error logging enabled
    When various errors occur during operations
    Then detailed error information should be logged
    And stack traces should be available for debugging
    And error context should include operation details

  @user-friendly-errors
  Scenario: Provide user-friendly error messages
    Given I am building an application for end users
    When errors occur during DBF operations
    Then error messages should be clear and non-technical when appropriate
    And suggestions for resolution should be provided when possible
    And technical details should be available for developers

  @error-codes
  Scenario: Provide consistent error classification
    Given different types of errors can occur
    When I need to handle errors programmatically
    Then errors should be properly classified by type
    And consistent error codes should be available
    And error hierarchy should allow appropriate exception handling