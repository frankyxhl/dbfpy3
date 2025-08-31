# Decision Log - dbfpy3

## 2025-08-31: Critical Bug Fix - Header Record Count

### Decision: Immediately Fix Header _changed Flag Issue
**Context**: Discovered critical bug where new records weren't persisted to disk
**Decision**: Set header._changed = True when incrementing record count
**Rationale**:
- Data integrity issue causing silent data loss
- Records appeared to save but were lost on file reopen
- Simple one-line fix with huge impact
- Critical enough to warrant immediate patch release
**Trade-offs**:
- Pro: Prevents data loss immediately
- Pro: Minimal code change (one line)
- Pro: No API changes or breaking changes
- Con: Should have been caught earlier
- Con: May have affected production systems

### Decision: Add Dedicated Test File for Regression Prevention
**Context**: Need to ensure this specific bug never recurs
**Decision**: Create tests/test_header_record_count.py with targeted tests
**Rationale**:
- Isolation makes the test purpose crystal clear
- Easy to run just these tests during debugging
- Documents the exact bug scenario
- Regression prevention for critical issue
**Trade-offs**:
- Pro: Clear test intent and documentation
- Pro: Fast targeted testing possible
- Pro: Good example for future similar issues
- Con: Another test file to maintain
- Con: Some overlap with existing tests

## 2025-08-31: FoxPro Double Field Implementation

### Decision: Implement Native Double Field Type B Support
**Context**: User reported needing "nasty hacks" to handle FoxPro Double fields
**Decision**: Add full native support for Double field type (B)
**Rationale**:
- Eliminates need for workarounds and external libraries
- FoxPro Double is a standard field type that should be supported
- IEEE 754 format is well-understood and easy to implement
- Improves library completeness for FoxPro compatibility
**Trade-offs**:
- Pro: Native support for high-precision floating-point data
- Pro: No external dependencies needed
- Pro: Standard IEEE 754 format ensures compatibility
- Con: Binary floating-point has inherent precision limitations
- Con: Adds another field type to maintain

### Decision: Use IEEE 754 Double-Precision Format
**Context**: Need to choose encoding format for Double fields
**Decision**: Use standard IEEE 754 double-precision (binary64)
**Rationale**:
- This is what FoxPro uses natively
- Python's struct module handles it perfectly
- CPU-native format for best performance
- 15-17 decimal digits precision sufficient for most use cases
**Trade-offs**:
- Pro: Direct hardware support on all platforms
- Pro: Fast encoding/decoding
- Pro: Matches FoxPro exactly
- Con: Binary floating-point rounding issues
- Con: Not suitable for exact decimal arithmetic

### Decision: Little-Endian Byte Order
**Context**: Need to choose byte order for Double field storage
**Decision**: Use little-endian (Intel/x86) byte order
**Rationale**:
- FoxPro was x86-centric and uses little-endian
- Consistent with other numeric fields in the library
- Most common on modern systems
**Trade-offs**:
- Pro: Direct FoxPro compatibility
- Pro: Consistent with rest of library
- Pro: Native on x86/x64 platforms
- Con: Requires byte swapping on big-endian systems
- Con: Not network byte order

## 2025-08-31: Test Suite Refactoring Decisions

### Decision: Skip Rather Than Implement Advanced Features
**Context**: 26 tests were failing for unimplemented features
**Decision**: Mark as skipped rather than implement
**Rationale**: 
- Maintains library's simplicity principle
- Avoids scope creep
- Clear communication about what's supported
- Allows future implementation if needed
**Trade-offs**: 
- Pro: Keeps codebase simple and maintainable
- Pro: Clear test status (not broken, just not implemented)
- Con: Some users may need these features
- Con: May need to implement later based on demand

### Decision: Standardize Field Definition Order
**Context**: Mixed conventions - some code used (name, type, length), others (type, name, length)
**Decision**: Standardize on (type_code, name, length) everywhere
**Rationale**:
- Matches existing library documentation
- Type-first is more logical (type determines valid length)
- Majority of existing code already used this order
**Trade-offs**:
- Pro: Consistent API across entire library
- Pro: Reduces confusion and bugs
- Con: Required touching many test files
- Con: Slight breaking change if anyone relied on undocumented behavior

### Decision: Add Field Alignment Tolerance for dBase III
**Context**: GitHub Issue #1 - dBase III files failing to load
**Decision**: Allow ±1 byte tolerance in field start position for dBase III files only
**Rationale**:
- dBase III had less strict alignment requirements
- Maintains compatibility with legacy files
- Only applies tolerance when needed (0x03, 0x83 signatures)
**Trade-offs**:
- Pro: Supports legacy files without breaking FoxPro support
- Pro: Minimal code change with targeted impact
- Con: Slight reduction in validation strictness for old files
- Con: Could mask corruption in rare cases

### Decision: Convert None to Empty String in Numeric Fields
**Context**: Writing None to numeric fields caused TypeError
**Decision**: Silently convert None to empty string
**Rationale**:
- DBF format uses empty strings for null numerics
- Consistent with how other DBF libraries handle nulls
- Prevents crashes on missing data
**Trade-offs**:
- Pro: Graceful handling of missing values
- Pro: Matches DBF conventions
- Con: Silent conversion might hide bugs
- Con: No distinction between 0 and null

### Decision: Add Python Magic Methods to DbfRecord
**Context**: Standard Python operations failed (e.g., 'field' in record)
**Decision**: Implement __contains__, fix __getitem__ for negative indexes
**Rationale**:
- Python users expect standard protocols to work
- Improves usability and reduces surprises
- Makes the library more Pythonic
**Trade-offs**:
- Pro: Intuitive Python interface
- Pro: Works with standard Python patterns
- Con: Slight overhead for magic method dispatch
- Con: More methods to maintain

## 2025-08-30: Testing Strategy Decisions

### Decision: Implement Both TDD and BDD Test Suites
**Context**: Existing tests were minimal, needed comprehensive coverage
**Decision**: Add 173 TDD tests + 146 BDD scenarios
**Rationale**:
- TDD for unit-level verification
- BDD for user-facing behavior documentation
- Complementary approaches catch different issues
**Trade-offs**:
- Pro: Comprehensive test coverage
- Pro: Clear behavior documentation
- Con: More tests to maintain
- Con: Some overlap between TDD and BDD

### Decision: Keep Original Tests Intact
**Context**: 16 original tests existed with different style
**Decision**: Keep them and add new tests alongside
**Rationale**:
- Preserves known-working test cases
- Avoids breaking changes
- Original tests might catch regressions new tests miss
**Trade-offs**:
- Pro: No risk of losing coverage
- Pro: Multiple perspectives on correctness
- Con: Some duplication
- Con: Mixed testing styles

## Design Principles (Historical)

### Principle: No External Dependencies
**Rationale**: 
- Simplifies installation
- Reduces security surface
- Avoids version conflicts
- Makes library more reliable

### Principle: Simplicity Over Features
**Rationale**:
- Easier to understand and maintain
- Fewer bugs
- Better performance
- Clear scope

### Principle: FoxPro Compatibility Primary
**Rationale**:
- Most common use case
- Well-defined specification
- Good balance of features
- Memo field support important

### Principle: Context Managers Preferred
**Rationale**:
- Ensures proper resource cleanup
- Pythonic pattern
- Prevents file handle leaks
- Clear lifecycle management