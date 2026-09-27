import unittest

from c_string_escape_decoder import decode, DecodeError


class TestSimpleEscapes(unittest.TestCase):
    def test_plain_text_passes_through(self):
        self.assertEqual(decode("hello"), "hello")

    def test_newline_escape(self):
        self.assertEqual(decode("a\\nb"), "a\nb")

    def test_tab_escape(self):
        self.assertEqual(decode("a\\tb"), "a\tb")

    def test_backslash_escape(self):
        self.assertEqual(decode("a\\\\b"), "a\\b")

    def test_quote_escapes(self):
        self.assertEqual(decode("\\\""), '"')
        self.assertEqual(decode("\\'"), "'")

    def test_question_mark_escape(self):
        # \? exists to avoid trigraphs in C; we decode it to a literal ?.
        self.assertEqual(decode("\\?"), "?")

    def test_all_simple_escapes(self):
        self.assertEqual(decode("\\a\\b\\f\\n\\r\\t\\v\\0"),
                         "\a\b\f\n\r\t\v\0")


class TestOctal(unittest.TestCase):
    def test_one_digit_octal(self):
        self.assertEqual(decode("\\1"), chr(0o1))

    def test_three_digit_octal(self):
        self.assertEqual(decode("\\177"), chr(0o177))

    def test_octal_stops_at_three_digits(self):
        # \1234 is \123 followed by '4'
        self.assertEqual(decode("\\1234"), chr(0o123) + "4")

    def test_octal_stops_at_non_octal(self):
        self.assertEqual(decode("\\128"), chr(0o12) + "8")


class TestHex(unittest.TestCase):
    def test_one_digit_hex(self):
        self.assertEqual(decode("\\x9"), chr(0x9))

    def test_two_digit_hex(self):
        self.assertEqual(decode("\xff"), chr(0xFF))

    def test_hex_greedy(self):
        # C hex escapes are greedy: \x12g is byte 0x12 then 'g'.
        self.assertEqual(decode("\\x12g"), chr(0x12) + "g")

    def test_hex_uppercase(self):
        self.assertEqual(decode("\\xAB"), chr(0xAB))

    def test_hex_no_digits_raises(self):
        with self.assertRaises(DecodeError):
            decode("\\x")


class TestLineContinuation(unittest.TestCase):
    def test_backslash_newline_removed(self):
        self.assertEqual(decode("a\\\nb"), "ab")

    def test_backslash_crlf_removed(self):
        self.assertEqual(decode("a\\\r\nb"), "ab")


class TestErrors(unittest.TestCase):
    def test_trailing_backslash(self):
        with self.assertRaises(DecodeError):
            decode("abc\\")

    def test_unknown_escape(self):
        with self.assertRaises(DecodeError):
            decode("\\z")

    def test_empty_string(self):
        self.assertEqual(decode(""), "")


class TestMixed(unittest.TestCase):
    def test_mixed_sequence(self):
        self.assertEqual(decode("line1\\nline2\\t\\x41\\101"),
                         "line1\nline2\tAA")


if __name__ == "__main__":
    unittest.main()
