#encoding=utf-8
import os
import sys

bytes_size=100*1024*1024 #100Mb

def reverse(path):
	path_reverse=path+'.reverse'
	test=open(path_reverse,'w')
	test.close()
	r=open(path,'rb')
	size=os.path.getsize(path)
	bytes=bytes_size
	bytes_written=bytes
	while True:
		w=open(path_reverse,'r+b')
		s=r.read(bytes)
		if not s:
			break
		if len(s)<bytes:
			sw=s[::-1]
			w.write(sw)
			w.close()
			break
			
		space=' '
		rest=(size-bytes_written)
		length=bytes
		while True:
			if length<=rest:
				temp=' '*bytes
				w.write(temp)
				length+=bytes
			else:
				temp=' '*(rest-length+bytes)
				w.write(temp)
				break

		
		sw=s[::-1]
		w.write(sw)
		w.close()
		bytes_written+=bytes

	r.close()
	os.remove(path)


def reverse_back(path):
	pos=path.rfind('.')
	path_reverse=path[:pos]
	test=open(path_reverse,'w')
	test.close()
	r=open(path,'rb')
	size=os.path.getsize(path)
	bytes=bytes_size
	bytes_written=bytes
	while True:
		w=open(path_reverse,'r+b')
		s=r.read(bytes)
		if not s:
			break
		if len(s)<bytes:
			sw=s[::-1]
			w.write(sw)
			w.close()
			break
			
		space=' '
		#print size
		#print bytes_written
		rest=(size-bytes_written)
		length=bytes
		while True:
			if length<=rest:
				temp=' '*bytes
				w.write(temp)
				length+=bytes
			else:
				temp=' '*(rest-length+bytes)
				w.write(temp)
				break

		
		sw=s[::-1]
		w.write(sw)
		w.close()
		bytes_written+=bytes
	r.close()
	os.remove(path)

def guess(filename,num):
    r=open(filename,'rb')
    pos=filename.rfind('.')
    filename=filename[:pos]
    ext=""
    fileNameWithouExt=filename
    pos=filename.rfind('.')
    if(pos!=-1):
        fileNameWithouExt=filename[:pos]
        ext=filename[pos+1:]
    newfilename=fileNameWithouExt+'.orginal.'+ext
    
  
    f=open(newfilename,'wb')
    
    
    line=r.read(1000)
    
    a=list(line)
    number=0
    temp=0
    for b in a:
        temp=(ord(b)-num)%256 
        for i in range(256):
            if (255*i)%256==temp:
                a[number]=chr(i)
                number+=1
        
        
    newline="".join(a)
    f.write(newline)
    
        
    f.close()
    typ=magic.from_file(newfilename)
    print(typ)
    if typ=='Microsoft ASF' or typ=='ISO Media, Apple QuickTime movie' or typ=='ISO Media, MPEG v4 system, version 1' or typ=="ISO Media, MPEG v4 system, version 2":
        return 1
    else:
        return 0
              

if __name__=='__main__':
	reverse(sys.argv[1].strip())
