from pypy.conftest import gettestobjspace

class AppTestTextIO:
    def setup_class(cls):
        cls.space = gettestobjspace(usemodules=['_io'])

    def test_constructor(self):
        import _io
        r = _io.BytesIO(b"\xc3\xa9\n\n")
        b = _io.BufferedReader(r, 1000)
        t = _io.TextIOWrapper(b)
        t.__init__(b, encoding="latin1", newline="\r\n")
        assert t.encoding == "latin1"
        assert t.line_buffering == False
        t.__init__(b, encoding="utf8", line_buffering=True)
        assert t.encoding == "utf8"
        assert t.line_buffering == True
        assert t.readline() == u"\xe9\n"
        raises(TypeError, t.__init__, b, newline=42)
        raises(ValueError, t.__init__, b, newline='xyzzy')
        t = _io.TextIOWrapper(b)
        assert t.encoding

    def test_properties(self):
        import _io
        r = _io.BytesIO(b"\xc3\xa9\n\n")
        b = _io.BufferedReader(r, 1000)
        t = _io.TextIOWrapper(b)
        assert t.readable()
        assert t.seekable()

    def test_unreadable(self):
        import _io
        class UnReadable(_io.BytesIO):
            def readable(self):
                return False
        txt = _io.TextIOWrapper(UnReadable())
        raises(IOError, txt.read)

    def test_detach(self):
        import _io
        b = _io.BytesIO()
        f = _io.TextIOWrapper(b)
        assert f.detach() is b
        raises(ValueError, f.fileno)
        raises(ValueError, f.close)
        raises(ValueError, f.detach)
        raises(ValueError, f.flush)
        assert not b.closed
        b.close()

    def test_newlinetranslate(self):
        import _io
        r = _io.BytesIO(b"abc\r\ndef\rg")
        b = _io.BufferedReader(r, 1000)
        t = _io.TextIOWrapper(b)
        assert t.read() == u"abc\ndef\ng"

    def test_one_by_one(self):
        import _io
        r = _io.BytesIO(b"abc\r\ndef\rg")
        t = _io.TextIOWrapper(r)
        reads = []
        while True:
            c = t.read(1)
            assert len(c) <= 1
            if not c:
                break
            reads.append(c)
        assert u''.join(reads) == u"abc\ndef\ng"

class AppTestIncrementalNewlineDecoder:

    def test_newline_decoder(self):
        import _io
        def check_newline_decoding_utf8(decoder):
            # UTF-8 specific tests for a newline decoder
            def _check_decode(b, s, **kwargs):
                # We exercise getstate() / setstate() as well as decode()
                state = decoder.getstate()
                assert decoder.decode(b, **kwargs) == s
                decoder.setstate(state)
                assert decoder.decode(b, **kwargs) == s

            _check_decode(b'\xe8\xa2\x88', u"\u8888")

            _check_decode(b'\xe8', "")
            _check_decode(b'\xa2', "")
            _check_decode(b'\x88', u"\u8888")

            _check_decode(b'\xe8', "")
            _check_decode(b'\xa2', "")
            _check_decode(b'\x88', u"\u8888")

            _check_decode(b'\xe8', "")
            raises(UnicodeDecodeError, decoder.decode, b'', final=True)

            decoder.reset()
            _check_decode(b'\n', "\n")
            _check_decode(b'\r', "")
            _check_decode(b'', "\n", final=True)
            _check_decode(b'\r', "\n", final=True)

            _check_decode(b'\r', "")
            _check_decode(b'a', "\na")

            _check_decode(b'\r\r\n', "\n\n")
            _check_decode(b'\r', "")
            _check_decode(b'\r', "\n")
            _check_decode(b'\na', "\na")

            _check_decode(b'\xe8\xa2\x88\r\n', u"\u8888\n")
            _check_decode(b'\xe8\xa2\x88', u"\u8888")
            _check_decode(b'\n', "\n")
            _check_decode(b'\xe8\xa2\x88\r', u"\u8888")
            _check_decode(b'\n', "\n")

        def check_newline_decoding(decoder, encoding):
            result = []
            if encoding is not None:
                encoder = codecs.getincrementalencoder(encoding)()
                def _decode_bytewise(s):
                    # Decode one byte at a time
                    for b in encoder.encode(s):
                        result.append(decoder.decode(b))
            else:
                encoder = None
                def _decode_bytewise(s):
                    # Decode one char at a time
                    for c in s:
                        result.append(decoder.decode(c))
            assert decoder.newlines == None
            _decode_bytewise(u"abc\n\r")
            assert decoder.newlines == '\n'
            _decode_bytewise(u"\nabc")
            assert decoder.newlines == ('\n', '\r\n')
            _decode_bytewise(u"abc\r")
            assert decoder.newlines == ('\n', '\r\n')
            _decode_bytewise(u"abc")
            assert decoder.newlines == ('\r', '\n', '\r\n')
            _decode_bytewise(u"abc\r")
            assert "".join(result) == "abc\n\nabcabc\nabcabc"
            decoder.reset()
            input = u"abc"
            if encoder is not None:
                encoder.reset()
                input = encoder.encode(input)
            assert decoder.decode(input) == "abc"
            assert decoder.newlines is None

        encodings = (
            # None meaning the IncrementalNewlineDecoder takes unicode input
            # rather than bytes input
            None, 'utf-8', 'latin-1',
            'utf-16', 'utf-16-le', 'utf-16-be',
            'utf-32', 'utf-32-le', 'utf-32-be',
        )
        import codecs
        for enc in encodings:
            decoder = enc and codecs.getincrementaldecoder(enc)()
            decoder = _io.IncrementalNewlineDecoder(decoder, translate=True)
            check_newline_decoding(decoder, enc)
        decoder = codecs.getincrementaldecoder("utf-8")()
        decoder = _io.IncrementalNewlineDecoder(decoder, translate=True)
        check_newline_decoding_utf8(decoder)

    def test_newline_bytes(self):
        import _io
        # Issue 5433: Excessive optimization in IncrementalNewlineDecoder
        def _check(dec):
            assert dec.newlines is None
            assert dec.decode(u"\u0D00") == u"\u0D00"
            assert dec.newlines is None
            assert dec.decode(u"\u0A00") == u"\u0A00"
            assert dec.newlines is None
        dec = _io.IncrementalNewlineDecoder(None, translate=False)
        _check(dec)
        dec = _io.IncrementalNewlineDecoder(None, translate=True)
        _check(dec)
