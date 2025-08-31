# language: en
@data-integrity @reliability
Feature: Data Integrity and Consistency
  As a developer storing critical business data
  I want to ensure data integrity and consistency in DBF files
  So that data remains accurate and reliable across all operations

  Background:
    Given I am working with data integrity requirements
    And I have access to the dbfpy3 library with integrity features

  @critical @write-read-consistency
  Scenario: Ensure data consistency across write-read cycles
    Given I have a DBF file with various field types
    When I write a record with specific values:
      | Field        | Value                           |
      | ID           | 12345                          |
      | NAME         | Test Customer with Ümlauts     |
      | AMOUNT       | 1234.5678                      |
      | ACTIVE       | true                           |
      | CREATED_DATE | 2023-12-31                     |
    And I close and reopen the file
    And I read the record back
    Then all field values should match exactly
    And numeric precision should be preserved
    And text content should be identical
    And boolean values should be consistent
    And dates should maintain their original values

  @precision @numeric-integrity
  Scenario: Maintain numeric precision and accuracy
    Given I have a DBF file with numeric fields of various precision
    When I store numeric values with different decimal places:
      | Field      | Type | Decimals | Test Value    |
      | PRICE      | N    | 2        | 99.99         |
      | PERCENTAGE | N    | 4        | 12.3456       |
      | INTEGER    | N    | 0        | 999999        |
      | TINY       | N    | 6        | 0.000001      |
    And I retrieve these values
    Then decimal precision should be maintained exactly
    And rounding should occur only at the specified decimal places
    And integer values should remain whole numbers
    And very small decimal values should be preserved

  @encoding @character-integrity
  Scenario: Preserve character encoding integrity
    Given I have a DBF file configured for specific character encoding
    When I store text with special characters:
      | Language | Text Sample                    |
      | English  | Standard ASCII text            |
      | German   | Äpfel, Öl, Übergabe           |
      | French   | Café, Naïve, Résumé           |
      | Spanish  | Niño, Señor, Corazón          |
    And I read the text back from the file
    Then all special characters should be preserved
    And character encoding should remain consistent
    And no character substitution should occur
    And text length should be maintained

  @boundary-values @edge-cases
  Scenario: Handle boundary values correctly
    Given I have a DBF file with fields of specific sizes
    When I store boundary values:
      | Field Type | Size | Boundary Value          |
      | Character  | 1    | X                       |
      | Character  | 255  | [255 character string]  |
      | Numeric    | 15,2 | 9999999999999.99        |
      | Numeric    | 15,2 | -9999999999999.99       |
      | Numeric    | 5,0  | 99999                   |
      | Date       | 8    | 1900-01-01              |
      | Date       | 8    | 2099-12-31              |
    Then all boundary values should be stored correctly
    And no overflow or underflow should occur
    And values should be retrievable without corruption

  @transaction-integrity @atomic-operations
  Scenario: Ensure atomic write operations
    Given I have a DBF file with existing records
    When I begin a series of related record updates
    And one of the updates encounters an error
    Then either all updates should complete successfully
    Or all updates should be rolled back to the original state
    And the file should not be left in a partially updated state
    And subsequent operations should work on consistent data

  @concurrent-integrity @multi-access
  Scenario: Maintain integrity during concurrent access
    Given I have a DBF file that may be accessed concurrently
    When multiple processes attempt to read the same data
    Then all processes should see consistent data
    When one process is writing while another is reading
    Then readers should not see partial updates
    And data corruption should not occur
    And appropriate locking mechanisms should prevent conflicts

  @large-data @volume-integrity
  Scenario: Maintain integrity with large data volumes
    Given I have a DBF file designed for large data sets
    When I add 10000 records to the file
    And I perform random access operations across the dataset
    Then record integrity should be maintained throughout
    And index positions should remain accurate
    And no data corruption should occur in any records
    And file header information should remain consistent

  @date-integrity @temporal-data
  Scenario: Ensure date and temporal data integrity
    Given I have a DBF file with date fields
    When I store dates spanning different centuries:
      | Date        | Format       | Expected Storage |
      | 1900-01-01  | ISO format   | Valid date       |
      | 2000-02-29  | Leap year    | Valid date       |
      | 2023-12-31  | Year end     | Valid date       |
      | 2024-02-29  | Leap year    | Valid date       |
    And I retrieve these dates
    Then all dates should be stored in correct format
    And leap years should be handled correctly
    And century transitions should be preserved
    And no date arithmetic errors should occur

  @field-overflow @data-truncation
  Scenario: Handle field overflow and truncation predictably
    Given I have a DBF file with limited field sizes
    When I attempt to store data exceeding field capacity:
      | Field Type | Size | Oversized Data           | Expected Result |
      | Character  | 10   | This is too long text   | Truncated       |
      | Numeric    | 5,2  | 999.999                 | Rounded/Error   |
      | Character  | 1    | AB                      | Truncated       |
    Then the system should handle overflow predictably
    And truncation should occur in a defined manner
    And no data should extend beyond field boundaries
    And warnings should be provided for data loss

  @null-values @empty-data
  Scenario: Handle null and empty values consistently
    Given I have a DBF file with various field types
    When I store empty or null values:
      | Field Type | Empty Value | Expected Storage |
      | Character  | ""          | Empty string     |
      | Numeric    | null        | Default/Zero     |
      | Logical    | null        | Default/False    |
      | Date       | null        | Empty date       |
    And I read these values back
    Then null values should be handled consistently
    And empty values should be distinguishable from zero values
    And field types should determine appropriate defaults

  @checksum-validation @file-integrity
  Scenario: Validate overall file integrity
    Given I have a completed DBF file with known content
    When I perform a full integrity check
    Then the file header should be mathematically consistent
    And record count should match actual records
    And field definitions should align with record structure
    And no orphaned or corrupted records should exist
    And file size should match expected calculations

  @backup-restore @data-safety
  Scenario: Ensure data safety during backup and restore operations
    Given I have a DBF file with critical business data
    When I create a backup copy of the file
    And I restore from the backup
    Then all data should be identical to the original
    And no records should be lost or corrupted
    And file metadata should be preserved
    And the restored file should be fully functional

  @compression-integrity @storage-optimization
  Scenario: Maintain integrity with storage optimizations
    Given I have a DBF file with repetitive data patterns
    When the file undergoes storage optimization
    Then all data should remain accessible
    And record relationships should be preserved
    And no data compression artifacts should appear
    And file operations should continue normally

  @version-migration @format-integrity
  Scenario: Preserve data integrity during format migrations
    Given I have data in an older DBF format version
    When I migrate to a newer format version
    Then all data should transfer without loss
    And field types should be preserved or appropriately converted
    And metadata should be maintained
    And the migrated file should pass all integrity checks

  @recovery-integrity @error-recovery
  Scenario: Maintain data integrity during error recovery
    Given I have a DBF file that experiences unexpected interruption
    When I recover from the interruption
    Then recoverable data should remain intact
    And corrupted sections should be clearly identified
    And recovery should not introduce additional corruption
    And the file should be usable after recovery operations