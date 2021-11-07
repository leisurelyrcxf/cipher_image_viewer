import time
import os
import random
import math
import traceback
import re
import sys
from hash_func import md5
from reverse import reverse, reverse_back

def encrypt(dir, E, N, do_reverse=False):
    if os.path.isdir(dir):
        x=input("Do you really want to encrypt all the subdirectories of '%s', press y to continue...\n" % dir)
        if x != 'y' and x != 'Y':
            exit(1)
    encrypt_(dir, E, N, do_reverse)

def encrypt_(dir, E, N, do_reverse=False):
    try:
        if(os.path.isdir(dir)):
            files=os.listdir(dir)
            for f in files:
                if(dir[-1]=='/'):
                    pass
                else:
                    dir+='/'
                encrypt_(dir+f, E, N, do_reverse)
        elif(os.path.isfile(dir)):
            if os.path.splitext(dir)[1]==".py" or os.path.splitext(dir)[1]==".pyc" or os.path.splitext(dir)[1]==".tmp" or os.path.splitext(dir)[1]==".cipher" or os.path.splitext(dir)[1]==".chksum":
                return
            elif os.path.splitext(dir)[1]==".reverse":
                dir=reverse_back(dir)
                encrypt_single_file(dir, E, N, do_reverse)
            else:
                encrypt_single_file(dir, E, N, do_reverse)
        else:
            print("directory or file '%s' does not exist" % dir)
    except:
           print(traceback.format_exc())
           exit()

def encrypt_single_file(path, E, N, do_reverse=False):
    print("E: %d, N: %d" % (E, N))
    byte_read=1*1024*1024 # 1MB

    print("Processing now: \""+path+"\"")
    chksum=md5(path)
    if do_reverse:
        path = reverse(path)
    r=open(path,'rb')
    encrypted_fname=path+'.cipher'
    if os.path.isfile(encrypted_fname):
        x=input("overwritting existed file '%s', press y to continue...\n" % encrypted_fname)
        if x != 'y' and x != 'Y':
            exit(1)

    enwr=open(encrypted_fname,'wb')
    enwr.write(bytes("cchheecckkssuumm", encoding='utf8'))
    enwr.write(bytes(chksum, encoding='utf8'))
    size=os.path.getsize(path)
    
    startTimeStamp=time.clock()
    while True:
        SpeedTimeS=time.clock()
        buf=r.read(byte_read)
        
        if not buf:
            break
        
        a=list(buf)
        if N > 256*256:
            b=[0]*(int(len(a)/2)*3+len(a)%2)
            b[-1]=a[-1]
            j=0
        else:
            b=a

        i=0
        while True:
            if i+1 >= len(a):
                break

            ori1=int(a[i])
            ori2=int(a[i+1])
            ori=ori1*256+ori2

            if N < 256*256:
                if ori < N:
                    ori=pow(ori, E, N)
                    b[i]=ori>>8
                    b[i+1]=ori&255
            else:
                assert(ori < N)
                encoded=pow(ori, E, N)
                b[j]=encoded>>16
                remain=encoded&65535
                b[j+1]=remain>>8
                b[j+2]=remain&255
                j+=3
            i+=2
        enwr.write(bytes(b))
        pos=r.tell()
        SpeedTimeE=time.clock()
        SpeedTime=SpeedTimeE-SpeedTimeS
        time_remained=SpeedTime*(size-pos)/byte_read
        h=int(time_remained/3600)
        m=int(((int(time_remained))%3600)/60)
        s=(int(time_remained))%60
        
        print("has processed "+str(float(pos)/1000)+'kb, ' + "time remains %dh %dmin %ds" % (h,m,s))
        print("has processed "+str(float(r.tell())/1000)+'kb.\n')

    enwr.close()
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
    parser.add_argument('--rerverse', type=bool, dest='reverse', help='reverse blocks', default=False)
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    if args.dir == "":
        print("must provide dir/file name")
        parser.print_help()
        exit(1)
    if args.N > 256**3:
        print("N must be not greater than 256*256*256")
        exit(1)
    if args.N < 32*256:
        print("N must be not less than 32*256")
        exit(1)
    encrypt(args.dir.strip(), args.E, args.N, args.reverse)
  
