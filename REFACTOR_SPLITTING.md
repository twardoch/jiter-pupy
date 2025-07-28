# Plan for Splitting Large Code Files in `jiter-pupy`

This document outlines a meticulously detailed plan for splitting large Python code files within the `jiter-pupy` project into smaller, more focused modules. The primary goal is to improve code organization, readability, and maintainability without altering the existing functionality or API.

## Analysis of Largest Code Files (from `REFACTOR_FILELIST.txt`)

Based on the provided `REFACTOR_FILELIST.txt`, the largest Python code files are:

*   `src/jiter_pupy/parser.py` (16 KB) - Contains the core `JiterDecoder` class.
*   `src/jiter_pupy/jiter_old.py` (15 KB) - Appears to be an older, potentially unused, version of `jiter.py`.
*   `src/jiter_pupy/partial.py` (7 KB) - Contains logic for partial JSON parsing.
*   `src/jiter_pupy/jiter.py` (5 KB) - Contains the main `from_json` function and public API.
*   `src/jiter_pupy/exceptions.py` (5 KB) - Contains custom exception classes.

## Splitting Strategy

The strategy focuses on isolating distinct functionalities into their own modules, adhering to the Single Responsibility Principle where appropriate.

### 1. Handling `src/jiter_pupy/jiter_old.py`

**Current State:** This file appears to be an outdated or alternative implementation.

**Proposed Action:**
Verify if `src/jiter_pupy/jiter_old.py` is actively used or referenced anywhere in the project. If it is not, it should be removed to reduce codebase clutter and potential confusion. If it is used, its purpose needs to be clarified, and its functionality either integrated into the main `jiter.py` or properly documented as a separate, distinct component.

**Detailed Steps:**

1.  **Search for References:**
    *   Perform a global search for `jiter_old` within the project to identify any imports or references to this file.
    *   `grep -r "jiter_old" .` (or equivalent search tool).

2.  **Decision and Action:**
    *   **If no references are found:** Delete `src/jiter_pupy/jiter_old.py`.
    *   **If references are found:**
        *   Analyze the nature of the references.
        *   Consult with the project owner or team to understand its intended purpose.
        *   Based on the clarification, either:
            *   Refactor its relevant parts into `src/jiter_pupy/jiter.py` or other appropriate modules.
            *   Rename it to something more descriptive (e.g., `jiter_experimental.py`) and add clear documentation explaining its role.
            *   (For this plan, we will assume it's unused and can be removed.)

### 2. Refactoring `src/jiter_pupy/parser.py`

**Current State:** This file contains the `JiterDecoder` class, which is a subclass of `json.JSONDecoder` and encapsulates all the custom parsing logic, including float handling, constant parsing, and object/list processing with caching and duplicate key detection.

**Proposed Changes:**
The `_process_list_values_for_caching` method within `JiterDecoder` is a general helper for recursive list processing related to caching. Extracting this into a new `utils.py` module will improve modularity.

**Detailed Steps:**

1.  **Create `src/jiter_pupy/utils.py`:**
    *   Create a new file named `utils.py` in the `src/jiter_pupy/` directory.
    *   Add necessary imports to `utils.py`: `from typing import Any, List, Callable`, `from .caching import get_cache_mode`.

2.  **Move `_process_list_values_for_caching`:**
    *   Open `src/jiter_pupy/parser.py`.
    *   Cut the definition of the `_process_list_values_for_caching` method from the `JiterDecoder` class.
    *   Paste the function into `src/jiter_pupy/utils.py`.
    *   Rename the function to `process_list_values_for_caching` (remove the leading underscore as it will no longer be a private method of `JiterDecoder`).
    *   Modify the function signature to accept `cache_string_func: Callable[[bytes], str]` as an argument, as it currently uses `self.cache_string_func`. The `get_cache_mode()` call can remain as it's imported directly.

    ```python
    # src/jiter_pupy/utils.py
    from typing import Any, List, Callable
    from .caching import get_cache_mode

    def process_list_values_for_caching(lst: List[Any], cache_string_func: Callable[[bytes], str]) -> List[Any]:
        """Helper to process list values for 'all' caching mode, recursively."""
        new_list = []
        for item in lst:
            if isinstance(item, str) and get_cache_mode() == "all":
                new_list.append(cache_string_func(item.encode())) # Inefficient simulation
            elif isinstance(item, list):
                new_list.append(process_list_values_for_caching(item, cache_string_func)) # Recursive call
            elif isinstance(item, dict): # Dicts are handled by object_pairs_hook
                new_list.append(item) # Assume it's already processed
            else:
                new_list.append(item)
        return new_list
    ```

3.  **Update `src/jiter_pupy/parser.py`:**
    *   In `src/jiter_pupy/parser.py`, add the following import:
        ```python
        from .utils import process_list_values_for_caching
        ```
    *   Update all calls to `self._process_list_values_for_caching` within `JiterDecoder` (specifically in `_object_pairs_hook_normal` and `_object_pairs_hook_duplicate_keys`) to call the new standalone function, passing `self.cache_string_func` as an argument:
        ```python
        # Example within _object_pairs_hook_normal:
        # old: final_v = self._process_list_values_for_caching(v)
        # new: final_v = process_list_values_for_caching(v, self.cache_string_func)
        ```

### 3. Files `src/jiter_pupy/jiter.py`, `src/jiter_pupy/partial.py`, and `src/jiter_pupy/exceptions.py`

**Current State:**
*   `src/jiter_pupy/jiter.py`: Already imports `cache_clear` and `cache_usage` from `caching.py` and re-exports them. This is a good pattern for API exposure.
*   `src/jiter_pupy/partial.py`: Contains `parse_partial_json`, a self-contained unit.
*   `src/jiter_pupy/exceptions.py`: Contains `JiterError` and `format_json_decode_error`, a small and focused unit.

**Proposed Action:**
No splitting is recommended for these files at this time, as further division would likely lead to excessive fragmentation without significant benefits to readability or maintainability.

## Verification Steps

After implementing the changes, perform the following verification steps to ensure functionality remains intact:

1.  **Run All Tests:**
    *   Execute the entire test suite to confirm that no regressions have been introduced.
    *   `hatch run test` or `python -m pytest`

2.  **Run Benchmarks:**
    *   Execute benchmark tests to ensure performance has not degraded significantly.
    *   `hatch run bench`

3.  **Linting and Type Checking:**
    *   Run linting and type checking tools to ensure code quality and type correctness.
    *   `hatch run lint`
    *   `hatch run type-check`

4.  **Manual Inspection:**
    *   Review the modified files and their imports to ensure logical consistency and adherence to the new structure.

## Commit Strategy

Each logical refactoring step (e.g., handling `jiter_old.py`, extracting parser helpers) should ideally be a separate commit for easier review and rollback if necessary.
