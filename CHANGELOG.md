# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-commit functionality for saving local changes
- Comprehensive documentation in README.md with detailed usage examples
- Code structure examples and programmatic usage documentation

### Changed
- Updated parser implementation in `src/jiter_pupy/parser.py` for improved functionality

## [0.8.5] - 2025-03-05

### Added
- Initial release of jiter-pupy pure Python implementation
- Core functionality as a drop-in replacement for the Rust-based jiter
- Support for JSON parsing from bytes with API compatibility
- String caching with modes: "all", "keys", "none"
- Float handling modes: "float", "decimal", "lossless-float"
- Partial JSON parsing with modes: "on", "off", "trailing-strings"
- Duplicate key detection functionality
- Handling of Infinity and NaN values
- Detailed error messages with line and column information
- Comprehensive test suite
- GitHub Actions workflows for CI/CD

### Technical Implementation
- Pure Python implementation using only standard library
- Custom `JiterDecoder` based on `json.JSONDecoder`
- `LosslessFloat` class for preserving original float representations
- Global string cache for optimizing memory usage
- Partial JSON recovery system for handling incomplete data

## [0.8.4] - 2025-03-05

### Changed
- Package structure refinements
- Import system improvements

## [0.8.3] - 2025-03-05

### Changed
- Refactored package to maintain jiter-pupy package name while enabling jiter import
- Package naming adjustments for better compatibility

### Fixed
- Import compatibility issues

## Initial Development

### Added
- Project initialization
- Basic package structure
- Initial documentation and setup configuration