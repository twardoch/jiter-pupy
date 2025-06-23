# Custom error handling to match jiter
import json

class JiterError(ValueError):
    """
    Base class for jiter-pupy specific errors.
    Mimics ValueError as per original jiter.
    """
    def __init__(self, msg: str, doc: str, pos: int, lineno: int, colno: int):
        self.msg = msg
        self.doc = doc # The original JSON document (string form)
        self.pos = pos
        self.lineno = lineno
        self.colno = colno
        # Format message similar to json.JSONDecodeError but potentially with jiter's specific wording
        # Example: "Invalid syntax at line 1 column 5 (char 4)"
        # Jiter's format: "expected value at line 1 column 1"
        # or "control character (U+0000) found in string at line 1 column 18"
        # We need to adapt self.msg or create a new formatted message.
        # For now, let's try to make it somewhat compatible.
        # The message from json.JSONDecodeError is usually quite good.
        # Jiter's error messages are more specific to its parser states.
        # We will try to wrap json.JSONDecodeError and reformat its message if possible,
        # or generate messages in this style for new errors.

        # Replicating Rust jiter's error message style:
        # e.g. "expected value at line {lineno} column {colno}"
        #      "control character (U+XXXX) found in string at line {lineno} column {colno}"
        #      "invalid escape sequence `\\u` at line {lineno} column {colno}"
        #      "invalid unicode code point at line {lineno} column {colno}"
        #      "trailing comma at line {lineno} column {colno}" (not in stdlib)
        #      "invalid number at line {lineno} column {colno}"
        #      "recursion limit reached at line {lineno} column {colno}"
        #      "Detected duplicate key "{key_name}" at line {lineno} column {colno}"

        # For now, let's use a generic format based on the input `msg`
        # and the line/col info. The main `from_json` will be responsible
        # for creating the `msg` in the desired format.
        full_message = f"{self.msg} at line {self.lineno} column {self.colno}"
        super().__init__(full_message)

def format_json_decode_error(jde: json.JSONDecodeError, json_data_str: str) -> JiterError:
    """
    Converts a standard json.JSONDecodeError into a JiterError
    with a message format closer to the original jiter.
    """
    # Jiter's error messages are often more succinct or specific.
    # Example: json.JSONDecodeError: "Expecting value: line 1 column 1 (char 0)"
    # Jiter equivalent: "expected value at line 1 column 1"

    # This is a simple transformation. More complex mapping might be needed for specific errors.
    # For now, we'll try to use the message from JSONDecodeError but format it.
    # The `jde.msg` is the core part, e.g., "Expecting value", "Unterminated string", etc.

    # A simple approach: use jde.msg directly.
    # Jiter Rust errors:
    # - "expected value"
    # - "invalid type: string \"{\", expected object" (this is when using schema validation, not relevant here)
    # - "invalid value: string \"\", expected u64" (also schema)
    # - "trailing characters"
    # - "invalid syntax" (generic)
    # - "eof while parsing value"
    # - "eof while parsing string"
    # - "eof while parsing object"
    # - "eof while parsing array"
    # - "key must be a string"
    # - "control character (U+0000) found in string"
    # - "invalid escape sequence `\\u`"
    # - "invalid unicode code point"
    # - "invalid number"
    # - "recursion limit reached" (from python, not jiter rust directly)
    # - "duplicate key: `...`" (from jiter rust)

    # We can try to map some common jde.msg contents.
    # For now, let's keep it simple and use the original message but ensure line/col formatting.
    # The main challenge is that jde.msg already includes line/col info in its own format.
    # We want to present it as "message at line L column C".

    # Let's use the raw `jde.msg` and let JiterError constructor format it.
    # The key is to get the core message without the default line/col part from jde.msg.
    # jde.msg examples:
    # "Expecting value"
    # "Unterminated string starting at"
    # "Invalid \uXXXX escape"
    # "Extra data" (for trailing characters)

    # We'll take `jde.msg` as the base message for JiterError.
    # The JiterError class will then append " at line X column Y".
    return JiterError(jde.msg, json_data_str, jde.pos, jde.lineno, jde.colno)

# Example usage (conceptual, will be used in from_json):
# try:
#     json.loads(...)
# except json.JSONDecodeError as e:
#     raise format_json_decode_error(e, json_string) from e
#
# # For custom errors not from json.JSONDecodeError:
# # raise JiterError("Detected duplicate key \"foo\"", json_str, pos, line, col)

# It's important that the final error messages match what the original jiter produces.
# This might require specific message construction in the calling code (e.g., in JiterDecoder
# or the main from_json function) before creating the JiterError instance.
# For example, for duplicate keys:
# msg = f'Detected duplicate key "{key_name}"'
# raise JiterError(msg, json_data_str, approx_pos, approx_lineno, approx_colno)
# The line/col for duplicate keys from stdlib is hard, as the hook gets pairs.
# We'd only know after the fact, and stdlib doesn't provide precise start of duplicate key.
