# Decision Log - dbfpy3

## 2025-08-31: Pandas Integration Architecture

### Decision: Optional Pandas Dependency
**Context**: Adding pandas support while maintaining zero-dependency core
**Decision**: Make pandas an optional dependency with graceful fallback
**Alternatives Considered**:
- Make pandas required - rejected to preserve simplicity
- Create separate package - rejected due to maintenance overhead
- Use duck typing - rejected as too fragile

**Rationale**:
- Preserves zero-dependency nature for basic use cases
- Allows advanced features for data science users
- Clear error messages guide users to install pandas when needed

**Implementation**:
```python
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
```

### Decision: Type Mapping Strategy
**Context**: DBF has limited types vs pandas rich type system
**Decision**: Conservative defaults with user override capability
**Alternatives Considered**:
- Strict type mapping - rejected as too restrictive
- Automatic type inference - rejected as unpredictable
- User-required specifications - rejected as poor UX

**Rationale**:
- Prevents data loss with safe defaults
- Allows optimization via field_specs parameter
- Matches user expectations from similar libraries

**Trade-offs**:
- Pro: Data safety and predictability
- Con: Potentially larger files without optimization

### Decision: Chunked Processing Default
**Context**: DBF files can be very large (multi-GB)
**Decision**: Default chunk_size of 10,000 records
**Alternatives Considered**:
- No chunking - rejected due to memory issues
- Smaller chunks (1,000) - rejected as too slow
- Larger chunks (100,000) - rejected as memory risky

**Rationale**:
- Balances memory usage and performance
- Works well on typical hardware (4-8GB RAM)
- User configurable for specific needs

## 2025-08-31: Critical Bug Fix Approach

### Decision: Minimal Fix with Comprehensive Testing
**Context**: Data loss bug in header persistence
**Decision**: One-line fix with extensive test coverage
**Alternatives Considered**:
- Refactor entire header system - rejected as too risky
- Add auto-save mechanism - rejected as performance impact
- Change file access pattern - rejected as API breaking

**Rationale**:
- Minimal change reduces regression risk
- Comprehensive tests prevent future issues
- Quick release possible for critical fix

## 2025-08-30: Test Framework Selection

### Decision: TDD with unittest + BDD with behave
**Context**: Need comprehensive test coverage
**Decision**: Dual approach with unittest for units, behave for scenarios
**Alternatives Considered**:
- pytest only - rejected, wanted BDD documentation
- behave only - rejected, poor for unit testing
- No BDD - rejected, loses use case documentation

**Rationale**:
- unittest is built-in, no dependencies
- behave documents real-world usage
- Clear separation of concerns

## 2025-08-30: FoxPro Double Field Implementation

### Decision: IEEE 754 Double-Precision Format
**Context**: Need to support FoxPro type 'B' fields
**Decision**: Use struct module with '<d' format
**Alternatives Considered**:
- Custom binary implementation - rejected as error-prone
- Decimal type - rejected as not binary compatible
- Float32 - rejected as insufficient precision

**Rationale**:
- Exact FoxPro compatibility
- Hardware-accelerated on all platforms
- Standard Python struct module

## Historical Decisions

### Pure Python Implementation
**Context**: Library needs broad compatibility
**Decision**: No C extensions or external dependencies
**Rationale**:
- Works on any Python 3.x platform
- Easier installation and deployment
- Simpler maintenance

### Context Manager Support
**Context**: DBF files need proper resource cleanup
**Decision**: Implement __enter__ and __exit__ methods
**Rationale**:
- Pythonic API
- Ensures file handles are closed
- Prevents data corruption

### Record Iterator Pattern
**Context**: Processing large DBF files
**Decision**: Implement __iter__ on Dbf class
**Rationale**:
- Memory efficient (one record at a time)
- Natural Python iteration
- Works with all iteration tools