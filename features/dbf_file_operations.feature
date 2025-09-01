# language: en
@dbf-core @file-operations
Feature: DBF File Operations
  As a developer working with database files
  I want to create, read, and manage DBF files
  So that I can store and retrieve structured data efficiently

  Background:
    Given I am working with a clean test environment
    And I have access to the dbfpy3 library

  @smoke @critical
  Scenario: Create a new empty DBF file
    Given I want to create a new DBF file called "employees.dbf"
    When I create the file with basic field structure
      | Field Name | Type | Length | Decimals |
      | ID         | N    | 5      | 0        |
      | NAME       | C    | 30     | 0        |
    And I close the file
    Then the DBF file should exist on disk
    And the file should have a valid DBF header
    And the file should contain 2 field definitions

  @smoke @critical
  Scenario: Open an existing DBF file
    Given I have an existing DBF file "sample.dbf" with employee data
    When I open the existing file for reading
    Then I should be able to access the file structure
    And I should see the correct number of field definitions
    And I should be able to read the record count

  @regression
  Scenario: Add multiple field types to a new DBF file
    Given I want to create a comprehensive employee database
    When I create a DBF file with the following field definitions:
      | Field Name  | Type | Length | Decimals | Purpose           |
      | EMPLOYEE_ID | N    | 6      | 0        | Unique identifier |
      | FULL_NAME   | C    | 50     | 0        | Employee name     |
      | SALARY      | N    | 10     | 2        | Salary amount     |
      | IS_ACTIVE   | L    | 1      | 0        | Employment status |
      | HIRE_DATE   | D    | 8      | 0        | Date of hire      |
    And I save the file structure
    Then each field should be correctly defined in the header
    And the field types should match the specifications
    And the field lengths should be preserved accurately

  @critical
  Scenario: Write and read records to a DBF file
    Given I have a DBF file with employee structure
    When I add a new employee record with the following data:
      | Field       | Value              |
      | EMPLOYEE_ID | 12345              |
      | FULL_NAME   | John Smith         |
      | SALARY      | 75000.50           |
      | IS_ACTIVE   | true               |
      | HIRE_DATE   | 2023-01-15         |
    And I save the record to the file
    Then the record should be stored in the database
    And I should be able to retrieve the record by index
    And all field values should match the original data

  @regression
  Scenario: Handle multiple records in sequence
    Given I have a DBF file with employee structure
    When I add multiple employee records:
      | EMPLOYEE_ID | FULL_NAME    | SALARY   | IS_ACTIVE | HIRE_DATE  |
      | 1001        | Alice Jones  | 68000.00 | true      | 2022-03-10 |
      | 1002        | Bob Johnson  | 72000.25 | true      | 2022-06-20 |
      | 1003        | Carol Davis  | 65000.75 | false     | 2021-12-05 |
    And I save all records to the file
    Then the file should contain 3 records
    And I should be able to iterate through all records
    And each record should maintain its individual field values

  @critical
  Scenario: Use context manager for safe file operations
    Given I want to ensure proper resource management
    When I use the DBF file within a context manager
    And I perform file operations inside the context
    And the context manager closes automatically
    Then the file should be properly closed
    And no file handles should remain open
    And subsequent operations should work correctly

  @regression
  Scenario: Access records by index
    Given I have a DBF file with 5 employee records
    When I access the first record using index 0
    Then I should get the expected first employee data
    When I access the last record using index -1
    Then I should get the expected last employee data
    When I try to access an out-of-bounds index
    Then I should receive an appropriate error

  @edge-case
  Scenario: Handle empty field values gracefully
    Given I have a DBF file with various field types for empty value testing
    When I create a record with some empty values:
      | Field      | Value |
      | NAME       |       |
      | AMOUNT     |       |
      | ACTIVE     |       |
      | DATE_FIELD |       |
    And I save the record
    Then the empty values should be handled appropriately
    And the record should be retrievable
    And empty fields should have appropriate default values

  @performance
  Scenario: Process large numbers of records efficiently
    Given I have a DBF file ready for bulk operations
    When I add 1000 employee records in sequence
    And I iterate through all records
    Then the operations should complete within reasonable time
    And memory usage should remain stable
    And all records should be accessible

  @data-types
  Scenario Outline: Store and retrieve different data types
    Given I have a DBF file with field type <field_type>
    When I store a value <input_value> in the field
    And I retrieve the value from the field
    Then the retrieved value should be <expected_value>
    And the data type should be preserved correctly

    Examples:
      | field_type | input_value        | expected_value     |
      | Character  | "Hello World"      | "Hello World"      |
      | Numeric    | 12345              | 12345              |
      | Numeric    | 123.45             | 123.45             |
      | Logical    | true               | true               |
      | Logical    | false              | false              |
      | Date       | 2023-12-25         | (2023, 12, 25)     |

  @validation
  Scenario: Validate field name restrictions
    Given I want to create a DBF file with field definitions
    When I try to add a field with name longer than 10 characters
    Then I should receive a validation error
    When I try to add a field with invalid characters in the name
    Then I should receive a validation error
    When I add a field with a valid 10-character name
    Then the field should be accepted successfully

  @file-properties
  Scenario: Check file metadata and properties
    Given I have created a DBF file with sample data
    When I examine the file properties
    Then I should see the correct file signature
    And I should see the accurate record count
    And I should see the proper header length
    And I should see the correct record length
    And I should see the last update date

  @cleanup
  Scenario: Clean up temporary files after operations
    Given I have created temporary DBF files for testing
    When I complete my database operations
    And I close all file handles
    Then I should be able to delete the temporary files
    And no file locks should prevent cleanup
    And the system resources should be released