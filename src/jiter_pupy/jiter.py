from typing import Any, Literal, Union
import json

from .caching import (
    cache_clear as clear_cache_func,
    cache_usage as get_cache_usage_func,
    set_cache_mode,
    cache_string,
    get_cache_mode
)
from .exceptions import JiterError, format_json_decode_error
from .float_handling import LosslessFloat # Ensure this is the one from float_handling.py
from .parser import JiterDecoder
from .partial import parse_partial_json


# Main API functions matching the original jiter package

def from_json(
    json_data: bytes,
    /,
    *,
    allow_inf_nan: bool = True,
    cache_mode: Union[bool, Literal["all", "keys", "none"]] = "all",
    partial_mode: Union[bool, Literal["off", "on", "trailing-strings"]] = False,
    catch_duplicate_keys: bool = False,
    float_mode: Literal["float", "decimal", "lossless-float"] = "float",
) -> Any:
    """
    Parse input bytes into a JSON object, API compatible with the Rust `jiter.from_json`.
    """
    if not isinstance(json_data, bytes):
        raise TypeError("Input must be bytes")

    if cache_mode not in ("all", "keys", "none", True, False):
        raise ValueError(f"Invalid cache_mode: {cache_mode}")
    if partial_mode not in ("off", "on", "trailing-strings", True, False):
        raise ValueError(f"Invalid partial_mode: {partial_mode}")
    if float_mode not in ("float", "decimal", "lossless-float"):
        raise ValueError(f"Invalid float_mode: {float_mode}")

    set_cache_mode(cache_mode)

    _partial_mode_internal: str
    if partial_mode is True:
        _partial_mode_internal = "on"
    elif partial_mode is False:
        _partial_mode_internal = "off"
    else:
        _partial_mode_internal = partial_mode

    json_data_str: str
    try:
        json_data_str = json_data.decode('utf-8')
    except UnicodeDecodeError as ude:
        bad_byte_pos = ude.start
        line = json_data[:bad_byte_pos].count(b'\n') + 1
        col_offset = json_data[:bad_byte_pos].rfind(b'\n')
        col = bad_byte_pos - col_offset if col_offset != -1 else bad_byte_pos + 1

        # Try to match jiter's "invalid unicode code point" message if possible
        # For now, using a message that indicates position clearly.
        # Jiter: "invalid unicode code point at line {line} column {col}"
        # Python's default: "utf-8' codec can't decode byte 0xXX in position Y: invalid start byte"
        # The message "invalid unicode code point" is more general for various UTF-8 errors.
        msg = "invalid unicode code point" # Generalizing from jiter's error
        raise JiterError(
            msg,
            json_data.decode(errors='ignore'),
            bad_byte_pos,
            line,
            col
        ) from ude

    if not json_data_str and _partial_mode_internal == "off": # Empty string and not in partial mode
        # jiter raises "expected value at line 1 column 1" for empty input
        raise JiterError("expected value", "", 0, 1, 1)


    if _partial_mode_internal != "off":
        try:
            return parse_partial_json(
                json_data=json_data,
                partial_mode=_partial_mode_internal,
                allow_inf_nan=allow_inf_nan,
                catch_duplicate_keys=catch_duplicate_keys,
                float_mode=float_mode,
                cache_string_func=cache_string,
                lossless_float_constructor=LosslessFloat
            )
        except json.JSONDecodeError as jde:
            raise format_json_decode_error(jde, json_data_str) from jde
        except JiterError:
            raise
        # Any other exception from partial parsing should propagate

    # Standard (non-partial) parsing
    decoder = JiterDecoder(
        allow_inf_nan=allow_inf_nan,
        cache_mode=get_cache_mode(),
        catch_duplicate_keys=catch_duplicate_keys,
        float_mode=float_mode,
        lossless_float_constructor=LosslessFloat,
        cache_string_func=cache_string
    )

    try:
        return decoder.decode(json_data_str)
    except json.JSONDecodeError as jde:
        raise format_json_decode_error(jde, json_data_str) from jde
    except JiterError:
        raise
    except RecursionError as re:
        # Try to find line/col for recursion error if possible, though difficult.
        # Jiter: "recursion limit reached at line L column C"
        # For now, using placeholder line/col.
        # A simple way to get *some* position is to assume it's at the end of what was processed,
        # but that's not accurate for where the recursion depth was hit.
        # Using 1,1 as a general indicator that position is not accurately determined.
        raise JiterError("recursion limit reached", json_data_str, 0, 1, 1) from re


def cache_clear() -> None:
    """Reset the string cache. API compatible with `jiter.cache_clear`."""
    clear_cache_func()

def cache_usage() -> int:
    """Get the size of the string cache in bytes. API compatible with `jiter.cache_usage`."""
    return get_cache_usage_func()

# LosslessFloat is part of the public API and will be exposed via __init__.py
# __version__ will also be handled by __init__.py
