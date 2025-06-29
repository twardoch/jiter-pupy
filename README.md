# Jiter-Pupy: A Pure Python JSON Parser

Jiter-Pupy is a Python library that provides a pure Python, drop-in replacement for the [jiter](https://github.com/pydantic/jiter) Rust-based JSON parsing library. It offers full API compatibility with the original `jiter`, allowing developers to use it as a seamless alternative when a pure Python solution is preferred or required.

## Part 1: General Overview

### What is Jiter-Pupy?

Jiter-Pupy is a high-fidelity Python implementation of the `jiter` JSON parsing interface. It focuses on providing the same features and behaviors as the original Rust version but using only standard Python capabilities. This means you can parse JSON data from bytes into Python objects with fine-grained control over aspects like string caching, float representation, and handling of incomplete or non-standard JSON.

### Who is it for?

*   **Python Developers**: Anyone working with JSON data in Python who needs the specific features of `jiter`.
*   **Users of `jiter`**: Those who are familiar with the `jiter` API and need a version that doesn't require a Rust compiler (e.g., for easier deployment in certain environments, or for use with Python interpreters like PyPy where C extensions might be less optimal or unavailable).
*   **Library Authors**: Developers who want to include `jiter`'s parsing capabilities as an optional backend without introducing a compiled dependency.

### Why is it useful?

*   **API Compatibility**: Acts as a direct substitute for the Rust-based `jiter`, meaning minimal to no code changes are needed if you're migrating.
*   **Pure Python**: No compilation steps are required for installation. This simplifies deployment, especially in environments where building Rust code might be problematic (e.g., restricted build systems, diverse target platforms).
*   **Portability**: Runs wherever Python runs, including CPython and PyPy.
*   **Feature-Rich Parsing**: Implements `jiter`'s advanced features:
    *   **String Caching**: Optimizes memory and potentially parsing speed for JSON documents with many repeated string values or keys.
    *   **Flexible Float Handling**: Allows parsing of floats as standard Python `float`, `Decimal` for exact precision, or `LosslessFloat` to preserve the original string representation of numbers.
    *   **Partial JSON Parsing**: Can robustly parse incomplete JSON documents, useful for streaming or recovering data from truncated inputs.
    *   **Error Handling**: Provides detailed error messages, including line and column numbers, compatible with `jiter`'s error reporting.
    *   **Duplicate Key Detection**: Can optionally raise errors if duplicate keys are found within a JSON object.

### How to Install

You can install Jiter-Pupy using pip:

```bash
pip install jiter-pupy
```

### How to Use

#### Programmatic Usage

Jiter-Pupy is used by importing the `jiter_pupy` package. For convenience, you might alias it to `jiter` to match the original library's usage:

```python
import jiter_pupy as jiter
from decimal import Decimal

# Basic JSON parsing
data_bytes = b'{"name": "Alice", "age": 30, "city": "Wonderland"}'
parsed_data = jiter.from_json(data_bytes)
print(parsed_data)
# Output: {'name': 'Alice', 'age': 30, 'city': 'Wonderland'}

# --- Feature Examples ---

# 1. Float Handling
float_data = b'{"value": 123.456789e-5}'
# Default (float)
print(jiter.from_json(float_data)['value'])
# Output: 0.00123456789

# Decimal
data_decimal = jiter.from_json(float_data, float_mode="decimal")
print(data_decimal['value'])
# Output: Decimal('0.00123456789')
print(isinstance(data_decimal['value'], Decimal))
# Output: True

# LosslessFloat (preserves original string representation)
data_lossless = jiter.from_json(float_data, float_mode="lossless-float")
print(str(data_lossless['value'])) # Convert to string to see original form
# Output: '123.456789e-5'
print(type(data_lossless['value']))
# Output: <class 'jiter_pupy.float_handling.LosslessFloat'>

# 2. String Caching
# Caching is enabled by default ("all" mode)
jiter.cache_clear() # Clear cache for demonstration
json_with_duplicates = b'{"key1": "value1", "key2": "value1", "key3": "value2"}'
jiter.from_json(json_with_duplicates)
print(f"Cache usage after parsing: {jiter.cache_usage()} bytes")
# Output: Cache usage after parsing: ... (some positive number)

# Disable caching
jiter.cache_clear()
jiter.from_json(json_with_duplicates, cache_mode="none")
print(f"Cache usage with caching disabled: {jiter.cache_usage()} bytes")
# Output: Cache usage with caching disabled: 0 bytes

# Cache only keys
jiter.cache_clear()
jiter.from_json(json_with_duplicates, cache_mode="keys")
# ... check cache_usage() ...

# 3. Partial JSON Parsing
incomplete_json = b'{"name": "Bob", "details": {"status": "active", "items": ["item1", "ite'

# partial_mode = "on" (or True) - discards incomplete parts
parsed_partial_on = jiter.from_json(incomplete_json, partial_mode="on")
print(parsed_partial_on)
# Output: {'name': 'Bob', 'details': {'status': 'active', 'items': ['item1']}} (or similar, depending on where parser stops)

# partial_mode = "trailing-strings" - attempts to include incomplete strings
# Note: Behavior for complex partials can be intricate.
parsed_partial_trailing = jiter.from_json(incomplete_json, partial_mode="trailing-strings")
print(parsed_partial_trailing)
# Output might be: {'name': 'Bob', 'details': {'status': 'active', 'items': ['item1', 'ite']}}

# 4. Duplicate Key Detection
duplicate_key_json = b'{"id": 1, "name": "Product", "id": 2}'
try:
    jiter.from_json(duplicate_key_json, catch_duplicate_keys=True)
except jiter.JiterError as e: # Or ValueError, as JiterError inherits from it
    print(e)
    # Output: Detected duplicate key 'id' at line 1 column X (or similar error)

# 5. Handling NaN/Infinity (allowed by default)
nan_inf_json = b'{"value1": Infinity, "value2": -Infinity, "value3": NaN}'
data_nan_inf = jiter.from_json(nan_inf_json)
print(data_nan_inf)
# Output: {'value1': inf, 'value2': -inf, 'value3': nan}

# Disallow NaN/Infinity
try:
    jiter.from_json(nan_inf_json, allow_inf_nan=False)
except jiter.JiterError as e: # Or ValueError
    print(e)
    # Output: Error related to unexpected token or value

```

#### Command Line Interface (CLI)

Jiter-Pupy is primarily a library and does not currently provide a standalone Command Line Interface.

## Part 2: Technical Details

### How Jiter-Pupy Works

Jiter-Pupy achieves API compatibility with the Rust `jiter` by internally using Python's standard `json` module, but with significant enhancements and custom logic wrapped around it.

1.  **Core Parsing**: The primary parsing function `from_json` takes `bytes` as input, as per the `jiter` API.
    *   The input bytes are first decoded to a UTF-8 string. If decoding fails, a `JiterError` is raised with positional information.
    *   An instance of `JiterDecoder` (a subclass of `json.JSONDecoder`) is used to parse the JSON string.

2.  **`JiterDecoder` (in `src/jiter_pupy/parser.py`)**: This custom decoder is the heart of the feature implementation.
    *   **Float Handling (`float_mode`)**:
        *   `"float"`: Uses Python's standard `float` type.
        *   `"decimal"`: Uses `Decimal` objects for parsing numbers, which is configured via the `parse_float` argument of `json.JSONDecoder`.
        *   `"lossless-float"`: Aims to create `LosslessFloat` objects. `LosslessFloat` (from `src/jiter_pupy/float_handling.py`) stores the original byte representation of the number. However, because `json.JSONDecoder` provides the number as a string to `parse_float`, the current implementation of `LosslessFloat` in `jiter-pupy` reconstructs this from the string. While this preserves the numerical value and string form for many cases, it's a known limitation that achieving true "lossless byte preservation" is challenging with the standard library's decoder alone, unlike a custom byte-level parser (like in Rust-jiter).
    *   **String Caching (`cache_mode`)**:
        *   Managed by functions in `src/jiter_pupy/caching.py`. A global dictionary `_string_cache` stores byte sequences and their decoded string counterparts.
        *   `"all"`: Both JSON keys and string values are cached.
        *   `"keys"`: Only JSON keys are cached.
        *   `"none"`: No caching is performed.
        *   The `JiterDecoder` attempts to use this cache. For keys, this is done in the `object_pairs_hook`. For string values, the current implementation notes challenges in perfectly integrating byte-level caching because the standard decoder's hooks receive already-decoded strings. The code includes "inefficient simulation" placeholders for where ideal byte-level caching would occur, highlighting this limitation. The caching functions (`cache_string`) expect bytes.
    *   **Duplicate Key Detection (`catch_duplicate_keys`)**: Implemented within the `object_pairs_hook` of `JiterDecoder`. It maintains a set of seen keys for the current object and raises a `JiterError` (via `json.JSONDecodeError` initially) if a duplicate is encountered. Precise line/column information for the *duplicate* key is challenging with `json.JSONDecoder` hooks.
    *   **NaN/Infinity Handling (`allow_inf_nan`)**: Controlled by providing a custom `parse_constant` to `json.JSONDecoder` which maps "Infinity", "-Infinity", and "NaN" strings to their corresponding float values if `allow_inf_nan` is true, or raises an error otherwise.

3.  **Partial Parsing (`partial_mode` in `src/jiter_pupy/partial.py`)**:
    *   If `partial_mode` is `"on"` or `True`, `parse_partial_json` attempts to parse the input. If it fails, it iteratively tries to parse progressively shorter prefixes of the JSON data until a valid JSON segment is found.
    *   If `partial_mode` is `"trailing-strings"`, the goal is to include incomplete strings at the end of the JSON. The current implementation for this is also challenging with `json.loads` and may behave similarly to `"on"` mode in many scenarios. A truly robust "trailing-strings" mode typically requires a stateful, custom parser that can identify and complete unterminated string tokens.
    *   If `partial_mode` is `"off"` or `False` (default), any incomplete JSON will result in an error.

4.  **Error Handling (`src/jiter_pupy/exceptions.py`)**:
    *   Defines a custom `JiterError` class (subclassing `ValueError` for compatibility with original `jiter` which also raises `ValueError`).
    *   A utility `format_json_decode_error` converts standard `json.JSONDecodeError` instances into `JiterError`, attempting to match the message style and detail (including line and column numbers) of the Rust `jiter` library.

5.  **Module Structure**:
    *   `__init__.py`: Exports the main public API (`from_json`, `cache_clear`, `cache_usage`, `LosslessFloat`, `__version__`).
    *   `jiter.py`: Contains the main `from_json` function and orchestrates calls to the parser and other modules.
    *   `parser.py`: Defines `JiterDecoder`.
    *   `caching.py`: Logic for string caching.
    *   `exceptions.py`: Custom error classes.
    *   `float_handling.py`: `LosslessFloat` class.
    *   `partial.py`: Logic for partial JSON parsing.
    *   `jiter_old.py`: Appears to be an older version or an alternative implementation approach, not directly part of the current primary logic flow.

### Coding and Contribution Rules

Jiter-Pupy follows standard Python development practices.

1.  **Code Style**:
    *   The project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Configuration is in `pyproject.toml`.
    *   Key aspects include adherence to PEP 8, with a line length of 88 characters.
    *   Run `hatch run fix` (or `hatch run lint fmt`) to automatically format and lint your code.

2.  **Type Hinting**:
    *   The codebase uses type hints extensively.
    *   [Mypy](http://mypy-lang.org/) is used for static type checking, configured in `pyproject.toml`.
    *   Ensure your contributions are fully type-hinted and pass `hatch run lint typing` (or `hatch run type-check`).

3.  **Testing**:
    *   Tests are written using [pytest](https://docs.pytest.org/).
    *   Test files are located in the `tests/` directory.
    *   Run tests with `hatch run test`.
    *   Ensure comprehensive test coverage for any new features or bug fixes. Check coverage with `hatch run test-cov`.
    *   The project aims for behavior parity with the Rust `jiter` library. Tests should reflect this, and where behavior might differ due to implementation constraints (e.g., `LosslessFloat` details), this should be understood or documented.

4.  **Development Environment**:
    *   [Hatch](https://hatch.pypa.io/) is used for managing development environments and running common tasks (linting, testing, building).
    *   Set up your environment using `hatch shell`.
    *   See `pyproject.toml` under `[tool.hatch.envs...scripts]` for available commands.

5.  **Dependencies**:
    *   Jiter-Pupy aims to have no runtime dependencies beyond the Python standard library.
    *   Development dependencies (linters, test runners) are managed via `hatch` and listed in `pyproject.toml`.

6.  **Commit Messages**:
    *   Follow conventional commit message guidelines (e.g., a concise subject line, followed by a more detailed body if necessary).

7.  **Pull Requests**:
    *   Contributions should be submitted as pull requests to the main repository.
    *   Ensure your PR passes all automated checks (linting, type checking, tests).
    *   Clearly describe the changes made and the reasoning behind them.

8.  **Versioning**:
    *   The project version is dynamically managed by `hatch-vcs` based on Git tags.

9.  **Known Limitations to Consider**:
    *   **LosslessFloat Byte Preservation**: As mentioned, perfectly replicating the byte-level preservation of `LosslessFloat` from the Rust version is challenging with Python's `json.JSONDecoder`. Contributions improving this within stdlib constraints would be valuable.
    *   **String Caching Precision**: True byte-level string caching (key and value) before decoding is difficult to inject into `json.JSONDecoder`. The current approach has limitations.
    *   **Error Position Accuracy**: While `JiterError` attempts to mimic `jiter` error messages, the exact character positions for some errors (like duplicate keys detected in hooks) might be harder to pinpoint accurately compared to a custom byte-level parser.
    *   **Performance**: While `jiter-pupy` implements features like caching, it is not expected to match the raw performance of the Rust-based `jiter`. The primary goal is API compatibility and pure Python portability.

By adhering to these guidelines, contributors can help maintain the quality, consistency, and reliability of Jiter-Pupy.
