# Core JSON parsing implementation for jiter_pupy
import json
from decimal import Decimal
from typing import Any, Callable, Dict, List, Tuple, Union

from .caching import cache_string, get_cache_mode
from .float_handling import LosslessFloat

# Type alias for JSON objects
JsonObject = Dict[str, Any]
JsonArray = List[Any]
JsonValue = Union[JsonObject, JsonArray, str, int, float, bool, None]

class JiterDecoder(json.JSONDecoder):
    def __init__(
        self,
        *,
        allow_inf_nan: bool,
        cache_mode: Union[bool, str], # Will be read via get_cache_mode
        catch_duplicate_keys: bool,
        float_mode: str,
        lossless_float_constructor: Callable[[bytes], LosslessFloat],
        cache_string_func: Callable[[bytes], str]
    ):
        self.allow_inf_nan = allow_inf_nan
        # cache_mode is handled by cache_string_func via get_cache_mode()
        self.catch_duplicate_keys = catch_duplicate_keys
        self.float_mode = float_mode
        self.lossless_float_constructor = lossless_float_constructor
        self.cache_string_func = cache_string_func

        # Determine the hooks based on parameters
        object_hook_to_use = None
        object_pairs_hook_to_use = None

        if self.catch_duplicate_keys:
            object_pairs_hook_to_use = self._object_pairs_hook_duplicate_keys
        else:
            # Default behavior if not catching duplicate keys, but still need to cache
            object_pairs_hook_to_use = self._object_pairs_hook_normal

        # Float mode handling might also need an object_hook if it involves transforming
        # values after they are initially parsed as floats/numbers.
        # LosslessFloat needs to be handled at a point where we have raw bytes,
        # which json.JSONDecoder doesn't easily expose for numbers.
        # This means parse_float might be the primary place for float_mode,
        # or we need a more complex object_hook that re-processes numbers.

        # For string caching on keys, object_pairs_hook is essential.
        # For string caching on values, object_hook can be used if it iterates through values.

        super().__init__(
            object_hook=object_hook_to_use, # We'll use object_pairs_hook primarily
            object_pairs_hook=object_pairs_hook_to_use,
            parse_float=self._parse_float,
            parse_int=self._parse_int, # For completeness, though not strictly modified by jiter options
            parse_constant=self._parse_constant,
            strict=True, # jiter is generally strict, though partial mode adds flexibility
        )
        # scanstring will be used by the decoder; we need to ensure our caching is applied
        # This is tricky because json.scanner.py_make_scanner is highly optimized C code
        # or pure Python that doesn't easily allow overriding string creation for values.
        # The object_hook/object_pairs_hook is a more viable path for values.
        # For keys, object_pairs_hook is perfect.

    def _parse_float(self, value: str) -> Any:
        """Handles float parsing according to float_mode."""
        if self.float_mode == "float":
            return float(value)
        elif self.float_mode == "decimal":
            return Decimal(value)
        elif self.float_mode == "lossless-float":
            # This is the tricky one. JSONDecoder gives us a string.
            # We need the original bytes to construct LosslessFloat.
            # This limitation means LosslessFloat might need to be handled
            # by a pre-processing step or a more complex parsing mechanism
            # if we can't get bytes here.
            # For now, we'll assume we can form it from string, though this loses the "exact bytes" aspect.
            # A true LosslessFloat from bytes would require direct access to the byte stream
            # during number parsing, which stdlib json.JSONDecoder doesn't offer.
            # The original jiter (Rust) can do this because it's a custom parser.
            # This is a known challenge from TODO.md.
            # We will store the string version, which is mostly fine for non-scientific notation.
            return self.lossless_float_constructor(value.encode()) # Pass as bytes
        else:
            # Should be validated before this point
            raise ValueError(f"Internal error: Invalid float_mode {self.float_mode}")

    def _parse_int(self, value: str) -> int:
        """Handles int parsing (standard)."""
        return int(value)

    def _parse_constant(self, value: str) -> Any:
        """Handles true, false, null, Infinity, NaN."""
        if value == "NaN":
            if self.allow_inf_nan:
                return float("nan")
            else:
                raise ValueError("NaN not allowed") # Or specific JiterError
        elif value == "Infinity":
            if self.allow_inf_nan:
                return float("inf")
            else:
                raise ValueError("Infinity not allowed") # Or specific JiterError
        elif value == "-Infinity": # json.decoder also handles this
            if self.allow_inf_nan:
                return float("-inf")
            else:
                raise ValueError("-Infinity not allowed") # Or specific JiterError
        # Standard constants are handled by superclass or default behavior if not overridden
        # For true, false, null, the default json.decoder behavior is fine.
        # This method is primarily for NaN/Infinity.
        # Python's json module handles "null", "true", "false" automatically.
        # It calls parse_constant for "NaN", "Infinity", "-Infinity".
        if value == 'null': return None
        if value == 'true': return True
        if value == 'false': return False
        # If it's none of the above, let the default decoder raise an error or handle it.
        # However, by defining _parse_constant, we take over.
        raise json.JSONDecodeError(f"Unexpected constant: {value}", "", 0)


    def _process_pair(self, key_bytes_or_str: Union[str, bytes], value: Any) -> Tuple[str, Any]:
        """Helper to cache/decode key and process value strings for caching if applicable."""
        key_str: str
        if isinstance(key_bytes_or_str, bytes): # Should always be str from decoder
            key_str = (
                self.cache_string_func(key_bytes_or_str)
                if get_cache_mode() in ["keys", "all"]
                else key_bytes_or_str.decode()
            )
        else: # is str
            # If it's already a string, it means the decoder produced it.
            # To enable key caching, we'd need it as bytes first.
            # This implies that for key caching to be effective with stdlib decoder,
            # we might need a more involved hook or a pre-scan.
            # For now, assume if it's str, it's already processed or not subject to byte-level caching.
            # However, the spirit of "keys" caching is to cache the bytes->str decoding.
            # The `scanstring` method of the decoder is responsible for string parsing.
            # If we get a `str` here, it's already been decoded.
            # This is a limitation if we want to cache `bytes -> str` for keys using only hooks.
            # Let's assume for now that keys from `object_pairs_hook` are always `str`.
            key_str = key_bytes_or_str
            # If cache_mode is "keys" or "all", we'd ideally cache it.
            # But we don't have the original bytes. This is a known limitation.

        # Process value if it's a string and cache_mode is "all"
        if isinstance(value, str) and (get_cache_mode() == "all"):
             # Similar to keys, `value` is already a `str`. We'd need original bytes.
             # This means `cache_string_func` which expects bytes won't directly apply here
             # unless we re-encode, which defeats the purpose.
             # This highlights the challenge of retrofitting byte-level caching onto stdlib decoder.
             # For now, we assume that if cache_mode is "all", strings passed through here
             # should be unique instances if they were meant to be cached.
             # The actual caching of value strings might need to happen if `scanstring`
             # itself could be configured to use our caching function.
             pass # Value string caching is difficult here without original bytes.

        if isinstance(value, dict): # It would be already processed by a nested call to object_pairs_hook
            pass
        elif isinstance(value, list):
            value = self._process_list(value)

        return key_str, value

    def _process_list(self, lst: JsonArray) -> JsonArray:
        """Recursively processes lists to ensure string values are cached if mode is 'all'."""
        new_list = []
        for item in lst:
            processed_item = item
            if isinstance(item, str) and (get_cache_mode() == "all"):
                # Again, item is already `str`. Caching `bytes -> str` is the goal.
                # This is a placeholder for where such caching would ideally occur.
                pass # String value caching difficulty
            elif isinstance(item, dict): # Already processed by object_pairs_hook
                pass
            elif isinstance(item, list):
                processed_item = self._process_list(item) # Recurse
            new_list.append(processed_item)
        return new_list

    def _object_pairs_hook_normal(self, pairs: List[Tuple[str, Any]]) -> JsonObject:
        """Default object_pairs_hook, applies caching."""
        # This hook receives keys as strings.
        # Caching for keys (bytes -> str) is hard here.
        # Caching for string values (bytes -> str) is also hard here as they are already decoded.
        # The main benefit here is applying recursive processing for nested structures.
        processed_pairs = []
        for k_str, v in pairs:
            # k_str is already a string. If get_cache_mode() is "keys" or "all",
            # we would ideally want to ensure this k_str came from our cache if its
            # original bytes were seen before. This is a limitation.
            # For v, similar logic applies if it's a string and cache_mode is "all".

            # Simulate caching by re-encoding and then decoding with cache_string_func
            # This is inefficient but demonstrates intent. A real solution needs parser access.
            final_k = k_str
            if get_cache_mode() == "keys" or get_cache_mode() == "all":
                 final_k = self.cache_string_func(k_str.encode()) # Inefficient simulation

            final_v = v
            if isinstance(v, str) and get_cache_mode() == "all":
                final_v = self.cache_string_func(v.encode()) # Inefficient simulation
            elif isinstance(v, list):
                final_v = self._process_list_values_for_caching(v)
            elif isinstance(v, dict): # It's already a dict from a nested call, so values are processed
                pass

            processed_pairs.append((final_k, final_v))
        return dict(processed_pairs)

    def _object_pairs_hook_duplicate_keys(self, pairs: List[Tuple[str, Any]]) -> JsonObject:
        """Handles duplicate key detection and caching."""
        # TODO: Actual line/col info for errors is a major challenge with stdlib.
        # We can only report that a duplicate was found.
        d: JsonObject = {}
        processed_pairs_for_dict_construction = []
        for k_str, v in pairs:
            final_k = k_str
            if get_cache_mode() == "keys" or get_cache_mode() == "all":
                final_k = self.cache_string_func(k_str.encode()) # Inefficient simulation

            if final_k in d:
                # TODO: Raise a more specific error with line/col if possible.
                # This requires knowing the byte offset, which JSONDecoder doesn't easily provide here.
                raise json.JSONDecodeError(f"Detected duplicate key '{final_k}'", "", 0) # Placeholder for pos

            final_v = v
            if isinstance(v, str) and get_cache_mode() == "all":
                final_v = self.cache_string_func(v.encode()) # Inefficient simulation
            elif isinstance(v, list):
                final_v = self._process_list_values_for_caching(v)
            elif isinstance(v, dict): # Already processed
                pass

            d[final_k] = final_v # Add to tracking dict
            processed_pairs_for_dict_construction.append((final_k, final_v))
        return d # Return the dict built this way

    def _process_list_values_for_caching(self, lst: List[Any]) -> List[Any]:
        """Helper to process list values for 'all' caching mode, recursively."""
        new_list = []
        for item in lst:
            if isinstance(item, str) and get_cache_mode() == "all":
                new_list.append(self.cache_string_func(item.encode())) # Inefficient simulation
            elif isinstance(item, list):
                new_list.append(self._process_list_values_for_caching(item))
            elif isinstance(item, dict): # Dicts are handled by object_pairs_hook
                new_list.append(item) # Assume it's already processed
            else:
                new_list.append(item)
        return new_list

    # Overriding decode to potentially pre-process json_data for things
    # like // comments or trailing commas if we were to support them (jiter does not explicitly).
    # For now, this is standard.
    def decode(self, s: str, _w: Any = json.decoder.WHITESPACE.match) -> Any:
        # If `s` is bytes, we need to decode it first. The main `from_json` should handle this.
        # Jiter's from_json takes bytes. This decoder expects str.

        # Note: The C-accelerated scanner might bypass some Python-level hooks or methods
        # if not carefully managed or if certain conditions are met.
        # Testing across Python versions and environments (with/without C extension) is important.

        # A critical part for LosslessFloat: if we use parse_float, it gets a string.
        # If we want true LosslessFloat (from original bytes), the stdlib decoder is insufficient.
        # This is a major known limitation noted in TODO.md.
        # The current LosslessFloat takes bytes, so _parse_float has to encode the string it gets.
        # This is not truly "lossless" if the string conversion (e.g. scientific notation) differs.

        # String caching:
        # The `json.scanner.make_scanner` (or its C equivalent) has `scanstring`.
        # This is where strings are decoded from the JSON input.
        # To apply our `cache_string(bytes_value) -> str` at the source,
        # we would need to replace or configure `scanstring`. This is not straightforward.
        # Hooks like `object_pairs_hook` get already-decoded strings.
        # The "inefficient simulation" above is a placeholder for this difficulty.
        # A "real" implementation of byte-level string caching with stdlib decoder
        # would likely require parsing the JSON string manually to identify byte sequences
        # for strings, then calling cache_string, then replacing them with markers,
        # and then letting json.loads parse that. This is very complex.
        # Or, accept that caching with stdlib will be on string objects themselves,
        # not necessarily on the byte->str decoding step.

        try:
            return super().decode(s, _w)
        except json.JSONDecodeError as e:
            # TODO: Enhance error messages to match jiter's format (line, col, message).
            # `e.lineno`, `e.colno`, `e.msg` are available.
            # This will be handled in exceptions.py and the main from_json.
            raise # Re-raise for now, will be caught by a wrapper.


# Example of how it might be called (simplified)
# decoder = JiterDecoder(
#     allow_inf_nan=True,
#     cache_mode="all", # This would be get_cache_mode()
#     catch_duplicate_keys=False,
#     float_mode="float",
#     lossless_float_constructor=LosslessFloat,
#     cache_string_func=cache_string # This is our caching.py's cache_string
# )
# result = decoder.decode(json_string)

# The main `from_json` function in `jiter.py` will instantiate and use this decoder.
