"""Decode C/C++ string escape sequences into raw characters.

Supported escapes (matching C11 6.4.4.4 character constant escape sequences):
  \\a  \\b  \\f  \\n  \\r  \\t  \\v  \\0  \\'  \\"  \\\\  \\?  \\newline
  \\ooo   octal, 1 to 3 octal digits
  \\xhh... hex, 1 or more hex digits (C allows arbitrary length)

Design decisions, stated plainly so the tests and the reader agree:
  - The input is the *contents* of a C string literal, without the surrounding
    double quotes. The caller is responsible for stripping them.
  - A backslash not followed by a recognised escape is an error. We do NOT
    silently drop the backslash (some compilers warn and pass it through); we
    raise. This is the one interpretation we picked.
  - Octal escapes read at most 3 digits. Hex escapes read greedily until a
    non-hex-digit is seen, matching C. This means "\x12g" decodes to the byte
    0x12 followed by 'g'.
  - Values are not range-checked against a specific char width. We return the
    integer value as a character via chr(). If the value exceeds 0x10FFFF a
    ValueError propagates; callers dealing with raw bytes should handle that.
  - A backslash immediately followed by a real newline (the physical line
    continuation in C source) is removed entirely.
"""


class DecodeError(ValueError):
    """Raised when an escape sequence is malformed."""


_SIMPLE = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
    "'": "'",
    '"': '"',
    "\\": "\\",
    "?": "?",
}


def _is_octal(c: str) -> bool:
    return "0" <= c <= "7"


def _is_hex(c: str) -> bool:
    return "0" <= c <= "9" or "a" <= c <= "f" or "A" <= c <= "F"


def decode(text: str) -> str:
    """Decode C/C++ escape sequences in *text*.

    *text* is the interior of a string literal (no surrounding quotes).
    Returns the decoded string. Raises DecodeError on a malformed escape.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        # We have a backslash. There must be a following character.
        if i + 1 >= n:
            raise DecodeError("trailing backslash at end of input")
        nxt = text[i + 1]

        # Line continuation: backslash + real newline vanishes.
        if nxt == "\n":
            i += 2
            continue
        if nxt == "\r":
            # Also accept \r\n and bare \r as line continuations, since C
            # source files may use either line ending.
            i += 2
            if i < n and text[i] == "\n":
                i += 1
            continue

        if nxt in _SIMPLE:
            out.append(_SIMPLE[nxt])
            i += 2
            continue

        if _is_octal(nxt):
            # Up to 3 octal digits.
            j = i + 1
            digits = []
            while j < n and len(digits) < 3 and _is_octal(text[j]):
                digits.append(text[j])
                j += 1
            value = int("".join(digits), 8)
            out.append(chr(value))
            i = j
            continue

        if nxt == "x":
            # One or more hex digits.
            j = i + 2
            digits = []
            while j < n and _is_hex(text[j]):
                digits.append(text[j])
                j += 1
            if not digits:
                raise DecodeError("\\x with no hex digits")
            value = int("".join(digits), 16)
            out.append(chr(value))
            i = j
            continue

        raise DecodeError(f"unknown escape: \\{nxt}")
    return "".join(out)
