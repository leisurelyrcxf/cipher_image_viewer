#encoding=utf-8
import os
import sys

def reverse(path):
    path_reverse=path+'.reverse'
    test=open(path_reverse,'w')
    test.close()
    _reverse(path, path_reverse)
    return path_reverse

def reverse_back(path_reverse):
    pos=path_reverse.rfind('.')
    path=path_reverse[:pos]
    test=open(path,'w')
    test.close()
    _reverse(path_reverse, path)
    return path

def _reverse(src, dst):
    block_size=100*1024*1024 #100Mb

    r=open(src, 'rb')
    size=os.path.getsize(src)
    bytes_written=block_size
    while True:
        w=open(dst, 'r+b')
        s=r.read(block_size)
        if not s:
            break

        if len(s)<block_size:
            w.write(s[::-1])
            w.close()
            break

        rest=(size-bytes_written)
        padding_length=0
        while True:
            if padding_length + block_size <= rest:
                w.write(bytes(' '*block_size, encoding='utf8'))
                padding_length += block_size
            else:
                if rest > padding_length:
                    w.write(bytes(' '*(rest-padding_length), encoding='utf8'))
                break
        w.write(s[::-1])
        w.close()
        bytes_written+=block_size
    r.close()
    os.remove(src)


if __name__=='__main__':
    path=sys.argv[1].strip()
    if path.endswith(".reverse"):
        reverse_back(path)
    else:
        reverse(path)
