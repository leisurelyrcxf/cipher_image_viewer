import time
import os
import random
def encrypt(path):
    '''
    while 1:
        filename=raw_input('input the file name for encryption: \n')
        try:
            r=open('C:\\Users\\ASUS\\Desktop\\'+filename,'rb')
            break
        except:
            print "file doesn't exist!"
    '''
    r=open(path,'rb')
    f=open(path+'.cipher','wb')
    randomseed=random.randint(0,40)
    startTimeStamp=time.clock()
    while 1 :
        buf=r.read(1000000)
        
        if not buf:
            break
        
        a=list(buf)
        number=0
        for b in a:
            a[number]=chr((ord(b)+randomseed)%256)
            number+=1
        newbuf="".join(a)
        
        
        f.write(newbuf)
        print "has processed "+str(float(r.tell())/1000)+'kb.\n'

    f.close()
    endTimeStamp=time.clock()
    print "Mission completed! Process totally %6.2f kb's document, cost %f seconds.\n"%((float(r.tell())/1000),endTimeStamp-startTimeStamp)


    
if __name__=="__main__":
    dir='D:\\workspace'
    files=os.listdir(dir)
    for f in files:
        encrypt(dir+os.sep+f)
