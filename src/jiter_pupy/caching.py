# String caching functionality for jiter_pupy
import sys
from typing import Dict, Union

# Global cache for strings
_string_cache: Dict[bytes, str] = {}
_cache_mode: Union[bool, str] = "all"  # "all", "keys", "none", True, False
_cache_usage: int = 0

def _get_sizeof_dict_entry(key: bytes, value: str) -> int:
    # Rough estimate of memory usage for a dict entry
    # This doesn't account for dict overhead itself, but tracks the stored items.
    return sys.getsizeof(key) + sys.getsizeof(value)

def cache_string(value: bytes) -> str:
    """
    Caches and returns a string if caching is enabled.
    """
    global _cache_usage
    if _cache_mode == "none" or _cache_mode is False:
        return value.decode()

    cached_value = _string_cache.get(value)
    if cached_value is None:
        decoded_value = value.decode()
        _string_cache[value] = decoded_value
        _cache_usage += _get_sizeof_dict_entry(value, decoded_value)
        return decoded_value
    return cached_value

def set_cache_mode(mode: Union[bool, str]) -> None:
    """
    Sets the string caching mode.
    Valid modes: "all", "keys", "none", True (same as "all"), False (same as "none").
    """
    global _cache_mode, _string_cache, _cache_usage
    if mode not in ("all", "keys", "none", True, False):
        raise ValueError(f"Invalid cache mode: {mode}")

    if mode is True:
        _cache_mode = "all"
    elif mode is False:
        _cache_mode = "none"
    else:
        _cache_mode = mode # type: ignore

    if _cache_mode == "none":
        cache_clear()

def get_cache_mode() -> Union[bool, str]:
    """Returns the current cache mode."""
    return _cache_mode

def cache_clear() -> None:
    """
    Clears the string cache.
    """
    global _string_cache, _cache_usage
    _string_cache.clear()
    _cache_usage = 0

def cache_usage() -> int:
    """
    Returns the current size of the string cache in bytes.
    """
    return _cache_usage

# Initialize with default mode
set_cache_mode("all")
