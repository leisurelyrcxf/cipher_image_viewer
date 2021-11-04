# -*- coding: cp936 -*-
import mimetypes
def guess(num):
    
    while 1:
        filename=raw_input('enter the file name for decrytion: \n')
        try:
            r=open('C:\\Users\\ASUS\\Desktop\\'+filename,'rb')
            break
        except:
            print "file doesn't exist!"
    pos=filename.rfind('.')
    filename=filename[:pos]
    ext=""
    fileNameWithouExt=filename
    pos=filename.rfind('.')
    if(pos!=-1):
        fileNameWithouExt=filename[:pos]
        ext=filename[pos+1:]
    newfilename='C:\\Users\\ASUS\\Desktop\\'+fileNameWithouExt+'.orginal.'+ext
  
    f=open(newfilename,'wb')
    
    
    line=r.read(100000)
    
    a=list(line)
    number=0
    #print a
    for b in a:
            
        a[number]=chr((ord(b)-num)%256)
        number+=1
    newline="".join(a)
    f.write(newline)
    
        
    f.close()
    if mimetypes.guess_type(newfilename)==('video/x-ms-wmv', None):
        return 1
    else:
        return 0
        
    
if __name__=='__main__':
    for i in range(50):
        if guess(i):
            break;
    print i
    
        

    
