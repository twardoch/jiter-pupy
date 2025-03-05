#!/usr/bin/env python3
"""
jiter_pupy: Pure Python implementation of jiter

A drop-in replacement for the jiter package that is API-compatible with the original Rust-based implementation,
but uses only Python's standard library json module.

This module re-exports everything from the jiter module to maintain backward compatibility.
"""
# this_file: src/jiter_pupy/__init__.py

import sys
from pathlib import Path

# Add the src directory to the Python path if needed
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import everything from jiter
try:
    from jiter import *  # noqa
    from jiter import __all__
except ImportError:
    # If jiter is not found, import directly from the jiter module in this package
    from jiter.jiter import (
        LosslessFloat,
        __version__,
        cache_clear,
        cache_usage,
        from_json,
    )

    __all__ = [
        "LosslessFloat",
        "__version__",
        "cache_clear",
        "cache_usage",
        "from_json",
    ]
