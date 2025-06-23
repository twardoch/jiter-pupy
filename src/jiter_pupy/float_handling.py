# Float handling (normal, decimal, lossless) for jiter_pupy
from decimal import Decimal

class LosslessFloat(float):
    """
    Represents a float from JSON, preserving the exact string representation.
    """
    def __init__(self, value: bytes):
        self._value_bytes = value
        # Validate that this is a valid float string and can be decoded
        try:
            decoded_value = self._value_bytes.decode('utf-8')
            # Check if it's a valid float number
            float(decoded_value)
        except UnicodeDecodeError as e:
            # Determine precise error location if possible (challenging from here)
            # Replicate jiter's error for consistency if possible
            # "invalid unicode code point at line 1 column X"
            # For direct instantiation, line/col is less relevant than the content itself.
            raise ValueError(f"LosslessFloat value is not valid UTF-8: {e}") from e
        except ValueError as e:
            # This means it decoded but wasn't a valid float number
            # Example: LosslessFloat(b"123.abc")
            # Jiter's error: "invalid number at line 1 column X"
            # We don't have line/col here, focus on "invalid number"
            raise ValueError(f"LosslessFloat value is not a valid number: {decoded_value}") from e
        super().__init__()

    def __float__(self) -> float:
        return float(self._value_bytes.decode())

    def __str__(self) -> str:
        return self._value_bytes.decode()

    def __repr__(self) -> str:
        return f"LosslessFloat('{self._value_bytes.decode()}')"

    def as_decimal(self) -> Decimal:
        return Decimal(self._value_bytes.decode())

    def __bytes__(self) -> bytes:
        return self._value_bytes
