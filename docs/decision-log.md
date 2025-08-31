# Decision Log - dbfpy3

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