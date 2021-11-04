import time
import os
import random
import math
import traceback
import re
import sys
from reverse import reverse

def encrypt(dir, R, N):
    print("R: %d, N: %d" % (R, N))
    try:
        if(os.path.isdir(dir)):
            files=os.listdir(dir)
            for f in files:
                if(dir[-1]=='/'):
                    pass
                else:
                    dir+='/'
                encrypt(dir+f, R, N)
        elif(os.path.isfile(dir)):
            if os.path.splitext(dir)[1]==".py" or os.path.splitext(dir)[1]==".pyc" or os.path.splitext(dir)[1]==".tmp" or os.path.splitext(dir)[1]==".cipher":
                return
            elif os.path.splitext(dir)[1]==".reverse":
                encrypt_reverse_file(dir, R, N)
            else:
                encrypt_single_file(dir, R, N)
        else:
            print("directory or file '%s' does not exist" % dir)
    except:
           print(traceback.format_exc())
           exit()

def encrypt_single_file(path, R, N):
    print("Processing now: \""+path+"\"")
    reverse(path)
    path=path+'.reverse'
    r=open(path,'rb')
    f=open(path+'.cipher','wb')
    size=os.path.getsize(path)
    
    startTimeStamp=time.clock()
    while 1 :
        SpeedTimeS=time.clock()
        byte_read=10000
        buf=r.read(byte_read)
        
        
        if not buf:
            break
        
        a=list(buf)
        i=0
        while True:
            if i>=len(a)-1:
                break
            
            ori1=int(a[i])
            ori2=int(a[i+1])
            ori=ori1*256+ori2
            if(ori<N):
                ori=pow(ori, R, N)
            
            ori1=ori/256
            ori2=ori%256
            a[i]=int(ori1)
            a[i+1]=int(ori2)
            i+=2
        f.write(bytes(a))
        pos=r.tell()
        SpeedTimeE=time.clock()
        SpeedTime=SpeedTimeE-SpeedTimeS
        time_remained=SpeedTime*(size-pos)/byte_read
        h=int(time_remained/3600)
        m=int(((int(time_remained))%3600)/60)
        s=(int(time_remained))%60
        
        print("has processed "+str(float(pos)/1000)+'kb, ' + "time remains %dh %dmin %ds" % (h,m,s))
        print("has processed "+str(float(r.tell())/1000)+'kb.\n')

    f.close()
    size=float(r.tell())
    r.close()
    os.remove(path)
    endTimeStamp=time.clock()
    print("The file \""+path+"\" has been encrypted successfully! Process totally %6.2f kb's document, cost %f seconds.\n"%((float(size)/1000),endTimeStamp-startTimeStamp))

def encrypt_reverse_file(path, R, N):
    if os.path.isfile(path+".cipher.tmp"):
        os.remove(path+".cipher")
        os.rename(path+".cipher.tmp", path+".cipher")
    print("Processing now: \""+path+"\"")
    r=open(path,'rb')
    size=os.path.getsize(path)
    f=open(path+".cipher"+".tmp", "wb")

    if os.path.isfile(path+'.cipher'):
        sizeCipher=os.path.getsize(path+'.cipher')
        fcipher=open(path+'.cipher','rb')
        sizeTemp=0
        while sizeTemp<sizeCipher-30000:
            byte_read=10000
            buf=fcipher.read(byte_read)
            r.read(byte_read)
            f.write(buf)
            sizeTemp+=byte_read
        fcipher.close()
    
    startTimeStamp=time.clock()
    while 1 :
        SpeedTimeS=time.clock()
        byte_read=10000
        buf=r.read(byte_read)
        
        
        if not buf:
            break
        
        a=list(buf)
        i=0
        while True:
            if i>=len(a)-1:
                break
            
            ori1=int(a[i])
            ori2=int(a[i+1])
            ori=ori1*256+ori2
            if(ori<N):
                ori=pow(ori, R, N)
            
            ori1=ori/256
            ori2=ori%256
            a[i]=int(ori1)
            a[i+1]=int(ori2)
            i+=2
        f.write(bytes(a))
        pos=r.tell()
        SpeedTimeE=time.clock()
        SpeedTime=SpeedTimeE-SpeedTimeS
        time_remained=SpeedTime*(size-pos)/byte_read
        h=int(time_remained/3600)
        m=int(((int(time_remained))%3600)/60)
        s=(int(time_remained))%60
        
        print("has processed "+str(float(pos)/1000)+'kb, ' + "time remains %dh %dmin %ds" % (h,m,s))
        print("has processed "+str(float(r.tell())/1000)+'kb.\n')

    f.close()
    size=float(r.tell())
    r.close()
    os.remove(path)
    os.remove(path+".cipher")
    os.rename(path+".cipher.tmp", path+".cipher")
    endTimeStamp=time.clock()
    print("The file \""+path+"\" has been encrypted successfully! Process totally %6.2f kb's document, cost %f seconds.\n"%((float(size)/1000),endTimeStamp-startTimeStamp))

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('-r', type=int, dest='R', help='R', default=53)
    parser.add_argument('-n', type=int, dest='N', help='N', default=61823)
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    if args.dir == "":
        print("must provide dir/file name")
        parser.print_help()
        exit(1)
    encrypt(sys.argv[1], args.R, args.N)
  
