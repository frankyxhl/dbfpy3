# language: en
@dbase3 @compatibility
Feature: dBase III Compatibility
  As a developer working with legacy database systems
  I want to maintain full compatibility with dBase III format files
  So that I can integrate with existing legacy applications and data

  Background:
    Given I am specifically working with dBase III format requirements
    And I have access to the dbfpy3 library with dBase III support

  @smoke @legacy
  Scenario: Create dBase III format file
    Given I want to create a file compatible with dBase III
    When I create a new DBF file with dBase III signature
    And I add standard dBase III field types:
      | Field Name | Type | Length | Purpose                    |
      | LEGACY_ID  | N    | 8      | Numeric identifier         |
      | COMPANY    | C    | 40     | Company name               |
      | AMOUNT     | N    | 10     | Financial amount with 2 decimals |
      | ACTIVE     | L    | 1      | Boolean flag               |
    And I save the file with dBase III format
    Then the file signature should be 0x03 or 0x83
    And the file should be readable by legacy dBase III applications
    And all field types should conform to dBase III standards

  @legacy @critical  
  Scenario: Read existing dBase III files
    Given I have an existing dBase III format file from a legacy system
    When I open the file using dbfpy3
    Then I should be able to read the dBase III header
    And I should correctly interpret the field definitions
    And I should access all records without data corruption
    And the character encoding should be handled properly

  @compatibility
  Scenario: Handle dBase III signature variations
    Given I need to work with different dBase III signature types
    When I encounter a file with signature 0x03 (dBase III without memo)
    Then I should be able to read the file correctly
    When I encounter a file with signature 0x83 (dBase III with memo)
    Then I should be able to read the file correctly
    And I should recognize the memo field capability

  @data-integrity
  Scenario: Preserve dBase III data format integrity
    Given I have a dBase III file with various field types
    When I read numeric fields from the legacy format
    Then decimal precision should be maintained correctly
    When I read character fields from the legacy format
    Then text padding and encoding should be preserved
    When I read logical fields from the legacy format
    Then boolean values should be interpreted correctly
    When I read date fields from the legacy format
    Then dates should be parsed in the correct format

  @interoperability
  Scenario: Roundtrip compatibility with legacy systems
    Given I have data created by a legacy dBase III application
    When I read the data using dbfpy3
    And I modify some records
    And I save the file back in dBase III format
    Then the legacy application should be able to read the modified data
    And no data corruption should occur during the roundtrip
    And file structure integrity should be maintained

  @field-types
  Scenario Outline: Handle dBase III specific field types
    Given I have a dBase III file with <field_type> field
    When I store a <field_type> value of <test_value>
    And I read the value back from the file
    Then the value should be <expected_result>
    And the format should comply with dBase III standards

    Examples:
      | field_type | test_value           | expected_result      |
      | Character  | "LEGACY SYSTEM"      | "LEGACY SYSTEM"      |
      | Numeric    | 999999               | 999999               |
      | Numeric    | 12345.67             | 12345.67             |
      | Logical    | T                    | true                 |
      | Logical    | F                    | false                |
      | Date       | "19951231"           | (1995, 12, 31)       |

  @encoding
  Scenario: Handle dBase III character encoding
    Given I have dBase III files with different character encodings
    When the file uses CP437 (original IBM PC) encoding
    Then special characters should be displayed correctly
    When the file uses CP850 (Western European) encoding  
    Then accented characters should be preserved
    When the file uses CP1252 (Windows Western) encoding
    Then extended characters should be handled properly

  @constraints
  Scenario: Respect dBase III format constraints
    Given I am creating a dBase III compatible file
    When I try to use field names longer than 10 characters
    Then the system should enforce the 10-character limit
    When I try to use more than 255 fields
    Then the system should enforce the field count limit
    When I try to create records larger than the format supports
    Then appropriate limits should be enforced

  @memo-fields
  Scenario: Handle memo field compatibility
    Given I have a dBase III file with memo field support
    When the file signature indicates memo capability (0x83)
    Then I should be able to access memo fields
    And memo data should be stored in associated .DBT file
    And memo field references should be maintained correctly
    When I read memo content
    Then the text should be preserved with correct formatting

  @header-format
  Scenario: Validate dBase III header format
    Given I am examining a dBase III file header
    When I check the header structure
    Then the file signature should be valid for dBase III
    And the record count should be accurately stored
    And the header length should match the field count
    And the record length should match field definitions
    And the modification date should be in dBase III format

  @error-recovery
  Scenario: Handle corrupted dBase III files gracefully
    Given I have a dBase III file with minor corruption
    When I attempt to open the corrupted file
    Then I should receive appropriate error messages
    And the system should not crash unexpectedly
    When the header is readable but records are corrupted
    Then I should be able to access the file structure
    And I should get clear warnings about data integrity issues

  @legacy-tools
  Scenario: Ensure compatibility with common dBase III tools
    Given I create a DBF file using dbfpy3 with dBase III format
    When I test the file with dBase III compatible tools
    Then the file should open without errors in dBASE III Plus
    And the file should be readable by FoxPro 2.x
    And the file should work with Clipper applications
    And modern tools should recognize it as valid dBase III format

  @version-detection
  Scenario: Automatically detect dBase III format version
    Given I have files from different dBase III versions
    When I open a file without specifying the version
    Then the system should automatically detect dBase III format
    And I should be able to query the detected version
    And appropriate compatibility mode should be activated
    And version-specific features should be handled correctly