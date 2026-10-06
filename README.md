# C String Escape Decoder

Decodes C/C++ string escape sequences (simple, octal, hex, line continuation) into their raw character form.

## Usage

```python
from c_string_escape_decoder import decode, DecodeError

decode("a\\nb")        # -> "a\nb"
decode("\\x41\\101")   # -> "AA"
decode("line\\\ncont")  # -> "linecont"

try:
    decode("\\z")
except DecodeError:
    pass
```

Pass the *interior* of the string literal — without the surrounding double quotes.

## Why

C source strings carry escapes that need to be resolved when you are parsing C
output, reading generated code, or consuming data emitted by a C program as a
string literal. This library does exactly that one job, with no dependencies.

The trade-off: an unrecognised escape (e.g. `\z`) raises `DecodeError` rather
than passing the backslash through. Some C compilers warn and emit the backslash
literally; we treat it as an error so silent corruption cannot slip through.

## Edge cases

- Octal escapes read at most 3 digits: `\1234` decodes to `\123` + `4`.
- Hex escapes are greedy: `\x12g` decodes to byte `0x12` + `g`.
- `\` followed by a real newline is a line continuation and is removed.
- `\x` with no hex digits raises `DecodeError`.
- A trailing backslash at end of input raises `DecodeError`.

## Exports

- `decode(text: str) -> str` — decode escapes in the given string.
- `DecodeError` — subclass of `ValueError`, raised on malformed input.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

