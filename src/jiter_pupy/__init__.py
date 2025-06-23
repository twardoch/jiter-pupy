#!/usr/bin/env python3
"""
jiter: Pure Python implementation of jiter

A drop-in replacement for the jiter package that is API-compatible with the original Rust-based implementation,
but uses only Python's standard library json module.
"""
# this_file: src/jiter_pupy/__init__.py

from .jiter import from_json, cache_clear, cache_usage
from .float_handling import LosslessFloat # Corrected import
from .__version__ import __version__ # Corrected import

__all__ = [
    "__version__", # Standard to list version first or early
    "from_json",
    "cache_clear",
    "cache_usage",
    "LosslessFloat",
]
