import os
import time
import sys
import traceback
import re
from reverse import reverse_back
from hash_func import md5
import portalocker

def decrypt(dire, D, N):
    try:
        if(os.path.isdir(dire)):
            if(dire[-1]=='/'):
                pass
            else:
                dire+='/'
            files=os.listdir(dire)
            for f in files:
                decrypt(dire+f, D, N)
        elif(os.path.isfile(dire)):
            if(re.search('^.*?\.reverse\.cipher$',dire)):
                decrypt_single_file(dire, D, N)
            else:
                print(dire+" Invalid file type")
        else:
            print("file doesn't exist")
    except:
        print(traceback.format_exc())
        return -1

        
def decrypt_single_file(filename, D, N):
    print("D: %d, N: %d" % (D, N))
    try:
        flag=0
        print("Processing now: \""+filename+"\"")
        startTimeStamp=time.clock()
        r=open(filename,'rb') #r stands for the file that is gonna be cyphered
        verify_chksum=False
        chksum_indication=r.read(16)
        if chksum_indication == b'cchheecckkssuumm':
            verify_chksum=True
            chksum=r.read(32)
            if len(chksum) < 32:
                print("checksum not correct")
                return
            chksum=chksum.decode('utf8')
        portalocker.lock(r, portalocker.LOCK_EX) #lock the file
        size=os.path.getsize(filename)
    
        index=filename.rfind('.')
        cypherfilename=filename[:index]  #get the name of the partly decrypted file
    
    
        byte_read=8*1024
        filetemp=''
        if(os.path.isfile(cypherfilename)):
            byte_processed=os.path.getsize(cypherfilename)  #get the size of file which has already been processed
            r0=open(cypherfilename,'rb')  #r0 stands for the read stream for partly decrpyted cypherfile
            index=cypherfilename.rfind('/')
            cypherfilenamefolderpath=cypherfilename[:index+1]
            cypherfilenamefilename=cypherfilename[index+1:]
            filetemp=cypherfilenamefolderpath+cypherfilenamefilename+'.temp'  #temp file for copy and decrpyt
            f=open(filetemp,'wb')  #write stream for temp file
            n=byte_processed/byte_read
            i=0
            while (1):
                if i>=n-2:
                      break
                line=r0.read(byte_read)
                if not line:
                    break
                r.read(byte_read)
                f.write(line)
                i+=1
            flag=1
    
        else:
            f=open(cypherfilename,'wb')
            flag=0

        while True:
            SpeedTimeS=time.clock()
            line=r.read(byte_read)
            if not line:
                break
            a=list(line)
            i=0
            while True:
                if i>=len(a)-1:
                    break
                ori1=int(a[i])
                ori2=int(a[i+1])
                ori=ori1*256+ori2
                if(ori<N):
                    ori=pow(ori, D, N)
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
            
        f.close()
        if(flag):
            r0.close()
            os.remove(cypherfilename)
            os.rename(filetemp,cypherfilename)
        portalocker.unlock(r)
        size=float(r.tell())
        r.close()
        reversed_filename=reverse_back(cypherfilename)
        if verify_chksum:
            reversed_file_chksum=md5(reversed_filename)
            if reversed_file_chksum == chksum:
                print("checksum match, removing cipher file %s" % filename)
                os.remove(filename)
            else:
                print("checksum mismatch")
                print("md5(%s): %s" % (reversed_filename, reversed_file_chksum))
                print("exp: %s" % chksum)
                return
        else:
            os.remove(filename)
        endTimeStamp=time.clock()
        print("The file \""+filename+"\" has been decrypted successfully. Process totally %6.2f kb's document, cost %f seconds.\n"%(size/1000,endTimeStamp-startTimeStamp))
    except:
        print(traceback.format_exc())
        if(flag):
            print("force quit manually")
            r0.close()
            portalocker.unlock(r)
            os.remove(cypherfilename)
            time.sleep(3)
            f.close()
            os.rename(filetemp,cypherfilename)
            return -1

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
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('-d', type=int, dest='D', help='D', default=1157)
    parser.add_argument('-n', type=int, dest='N', help='N', default=61823)
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    if args.dir == "":
        print("must provide dir/file name")
        parser.print_help()
        exit(1)
    decrypt(sys.argv[1].strip(), args.D, args.N)

