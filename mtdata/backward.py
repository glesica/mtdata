import os
from typing import BinaryIO, Iterable


def read_backward(file: BinaryIO) -> Iterable[str]:
    """
    Read the lines of a text file (opened in binary mode), but backward,
    from the last line to the first line.

    >>> from io import BytesIO
    >>> list(read_backward(BytesIO(b'a\\nb')))
    ['b', 'a\\n']
    >>> list(read_backward(BytesIO(b'a\\nb\\n')))
    ['b\\n', 'a\\n']
    >>> list(read_backward(BytesIO(b'a\\n\\n')))
    ['\\n', 'a\\n']
    >>> list(read_backward(BytesIO(b'\\n\\n')))
    ['\\n', '\\n']
    >>> list(read_backward(BytesIO(b'\\n')))
    ['\\n']
    >>> list(read_backward(BytesIO(b'')))
    []
    """
    file.seek(0, os.SEEK_END)
    length = file.tell()

    for offset in range(length - 1, -1, -1):
        file.seek(offset)

        if file.read(1) == b'\n':
            line = file.readline().decode()
            if line:
                yield line

        if offset == 0:
            file.seek(offset)
            yield file.readline().decode()
