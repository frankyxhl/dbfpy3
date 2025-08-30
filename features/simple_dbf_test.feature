# language: en
Feature: DBF Basic Functionality
  As a developer using the dbfpy3 library
  I want to create and read DBF files
  So that I can store structured data

  @smoke
  Scenario: Create a simple DBF file
    Given I have the dbfpy3 library available
    When I create a new DBF file with fields
    And I add a simple record
    And I close the file
    Then the file should exist and be readable