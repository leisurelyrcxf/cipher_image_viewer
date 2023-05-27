# encoding=utf-8
import os
import sys
from io import BytesIO

from send2trash import send2trash

block_size = 100 * 1024 * 1024  # 100Mb


def reverse(path):
    path_reverse = path + '.reverse'
    test = open(path_reverse, 'w')
    test.close()
    _reverse(path, path_reverse)
    return path_reverse


def reverse_back(path_reverse):
    pos = path_reverse.rfind('.')
    path = path_reverse[:pos]
    test = open(path, 'w')
    test.close()
    _reverse(path_reverse, path)
    return path


def _reverse(src, dst):
    r = open(src, 'rb')
    size = os.path.getsize(src)
    reverse_func(size, r, dst_opener=lambda mode: open(dst, mode))
    r.close()
    send2trash(src)


def reverse_func(size, reader, dst_opener=None, memory_output=False):
    bytes_written = block_size
    data = bytes()
    while True:
        if memory_output:
            w = BytesIO(data)
        else:
            w = dst_opener('r+b')

        s = reader.read(block_size)
        if not s:
            if memory_output:
                data = w.getvalue()
            w.close()
            break

        if len(s) < block_size:
            w.write(s[::-1])
            if memory_output:
                data = w.getvalue()
            w.close()
            break

        rest = (size - bytes_written)
        padding_length = 0
        while True:
            if padding_length + block_size <= rest:
                w.write(bytes(' ' * block_size, encoding='utf8'))
                padding_length += block_size
            else:
                if rest > padding_length:
                    w.write(bytes(' ' * (rest - padding_length), encoding='utf8'))
                break
        w.write(s[::-1])
        bytes_written += block_size
        if memory_output:
            data = w.getvalue()
        w.close()

    if memory_output:
        return data
    return None


if __name__ == '__main__':
    path = sys.argv[1].strip()
    if path.endswith(".reverse"):
        reverse_back(path)
    else:
        reverse(path)
