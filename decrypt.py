import os
import time
import sys
import traceback
import re
from reverse import reverse_back
import portalocker

def decrypt(dire, D, N):
    print("D: %d, N: %d" % (D, N))
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
    try:
        flag=0
        print("Processing now: \""+filename+"\"")
        startTimeStamp=time.clock()
        r=open(filename,'rb') #r stands for the file that is gonna be cyphered
        portalocker.lock(r, portalocker.LOCK_EX) #lock the file
        size=os.path.getsize(filename)
    
        index=filename.rfind('.')
        cypherfilename=filename[:index]  #get the name of the partly decrypted file
    
    
        byte_read=10000
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
        os.remove(filename)
        reverse_back(cypherfilename)
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

