import time
import os
import random
import math
import traceback
import re
import sys
from hash_func import md5
from reverse import reverse, reverse_back

def encrypt(dir, E, N, generate_chksum=True):
    try:
        if(os.path.isdir(dir)):
            files=os.listdir(dir)
            for f in files:
                if(dir[-1]=='/'):
                    pass
                else:
                    dir+='/'
                encrypt(dir+f, E, N, generate_chksum)
        elif(os.path.isfile(dir)):
            if os.path.splitext(dir)[1]==".py" or os.path.splitext(dir)[1]==".pyc" or os.path.splitext(dir)[1]==".tmp" or os.path.splitext(dir)[1]==".cipher" or os.path.splitext(dir)[1]==".chksum":
                return
            elif os.path.splitext(dir)[1]==".reverse":
                dir=reverse_back(dir)
                encrypt_single_file(dir, E, N, generate_chksum)
            else:
                encrypt_single_file(dir, E, N, generate_chksum)
        else:
            print("directory or file '%s' does not exist" % dir)
    except:
           print(traceback.format_exc())
           exit()

def encrypt_single_file(path, E, N, generate_chksum=True):
    print("E: %d, N: %d" % (E, N))
    byte_read=8*1024

    print("Processing now: \""+path+"\"")
    if generate_chksum:
        chksum=md5(path)
    path = reverse(path)
    r=open(path,'rb')
    f=open(path+'.cipher','wb')
    if generate_chksum:
        f.write(bytes("cchheecckkssuumm", encoding='utf8'))
        f.write(bytes(chksum, encoding='utf8'))
    size=os.path.getsize(path)
    
    startTimeStamp=time.clock()
    while 1 :
        SpeedTimeS=time.clock()
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
                ori=pow(ori, E, N)
            
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

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('-e', type=int, dest='E', help='E', default=53)
    parser.add_argument('-n', type=int, dest='N', help='N', default=61823)
    parser.add_argument('--unsafe', type=bool, dest='unsafe', help='unsafe mode, no checksum', default=False)
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    if args.dir == "":
        print("must provide dir/file name")
        parser.print_help()
        exit(1)
    if args.N > 65536:
        print("N must be not greater than 65536")
        exit(1)
    if args.N < 32*256:
        print("N must be not less than 32*256")
        exit(1)
    encrypt(sys.argv[1], args.E, args.N, not args.unsafe)
  
