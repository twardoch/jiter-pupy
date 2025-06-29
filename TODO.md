# Jiter-Pupy TODO List

## Critical Bug Fixes (Priority: High)

- [ ] Fix version import issue for mobile environments by implementing fallback version handling
- [ ] Add try/except block in __init__.py to handle missing __version__ module
- [ ] Embed fallback version string directly in __init__.py
- [ ] Test version import across different deployment scenarios (mobile, PyPy, etc.)

## Error Handling Improvements (Priority: High)

- [ ] Enhance JiterError with more precise line/column tracking
- [ ] Implement custom error context tracking during parsing
- [ ] Improve error message formatting to match jiter style exactly
- [ ] Add error recovery suggestions in error messages
- [ ] Fix imprecise duplicate key error location reporting

## String Caching Optimizations (Priority: High)

- [ ] Implement byte-level string caching pre-processing layer
- [ ] Create custom string interning system for better performance
- [ ] Add cache hit/miss rate metrics
- [ ] Optimize cache lookup performance with better data structures
- [ ] Fix inefficient string value caching simulation

## Performance Optimizations (Priority: Medium)

- [ ] Profile parser to identify performance bottlenecks
- [ ] Implement __slots__ for frequently created objects
- [ ] Add object pooling for common types
- [ ] Optimize Decimal creation for common float values
- [ ] Implement fast path for standard float parsing
- [ ] Add LRU eviction to string cache with configurable limits
- [ ] Optimize LosslessFloat string operations

## Testing Enhancements (Priority: High)

- [ ] Port all test cases from original Rust jiter
- [ ] Add property-based testing using Hypothesis
- [ ] Implement fuzzing tests for malformed JSON
- [ ] Add Unicode edge case tests
- [ ] Create stress tests for large JSON files
- [ ] Add performance regression tests
- [ ] Test with extremely large numbers and deeply nested structures
- [ ] Add memory exhaustion scenario tests
- [ ] Achieve >95% test coverage

## Partial Parsing Improvements (Priority: Medium)

- [ ] Improve "trailing-strings" mode implementation
- [ ] Add better incomplete JSON recovery logic
- [ ] Implement stateful parsing for better partial support
- [ ] Add more granular partial parsing options

## LosslessFloat Enhancements (Priority: Medium)

- [ ] Document limitations of LosslessFloat byte preservation
- [ ] Optimize LosslessFloat memory usage
- [ ] Add LosslessFloat arithmetic operations support
- [ ] Improve LosslessFloat string representation handling

## Documentation (Priority: Medium)

- [ ] Create API reference documentation
- [ ] Write migration guide from Rust jiter
- [ ] Add performance tuning guide
- [ ] Create comprehensive troubleshooting guide
- [ ] Document all error codes and messages
- [ ] Add more code examples for edge cases

## Deployment and Distribution (Priority: High)

- [ ] Test installation on Windows, macOS, and Linux
- [ ] Verify PyPy compatibility
- [ ] Test in containerized environments
- [ ] Create conda-forge package
- [ ] Test with Python 3.13 when available
- [ ] Add installation troubleshooting guide

## Benchmarking (Priority: Medium)

- [ ] Create comprehensive benchmark suite
- [ ] Compare performance with Rust jiter
- [ ] Track performance across Python versions
- [ ] Implement continuous performance monitoring
- [ ] Create performance comparison documentation

## Developer Experience (Priority: Low)

- [ ] Add JSON validation utilities
- [ ] Implement pretty-printing options
- [ ] Add debug mode with verbose output
- [ ] Create JSON schema validation support
- [ ] Add helper functions for common use cases

## Integration Testing (Priority: Medium)

- [ ] Test with Django REST framework
- [ ] Test with FastAPI
- [ ] Test with pandas JSON reading
- [ ] Test with requests library
- [ ] Create integration examples
- [ ] Document compatibility matrix

## Advanced Features (Priority: Low)

- [ ] Research streaming JSON parser implementation
- [ ] Add async/await support for parsing
- [ ] Implement custom object decoder hooks
- [ ] Add plugin system for extensibility
- [ ] Consider JSON serialization support
- [ ] Explore Cython optimization possibilities

## Code Quality (Priority: Medium)

- [ ] Add type stubs for better IDE support
- [ ] Improve mypy type coverage to 100%
- [ ] Add more inline documentation
- [ ] Refactor parser.py for better maintainability
- [ ] Clean up jiter_old.py or remove if unused

## Project Management (Priority: Low)

- [ ] Create contributor guidelines
- [ ] Set up issue templates
- [ ] Implement automated changelog generation
- [ ] Create project roadmap
- [ ] Set up project board for tracking
- [ ] Establish security policy

## Long-term Considerations

- [ ] Investigate pure Python JSON parser alternatives
- [ ] Research PyPy-specific optimizations
- [ ] Consider implementing custom tokenizer
- [ ] Explore WebAssembly compilation options
- [ ] Plan for Python 3.14+ features

---

Note: Tasks are roughly ordered by priority within each section. High-priority items should be addressed first to ensure stability and compatibility.