import os
import time
import sys
import traceback
import re
from reverse import reverse_back, reverse_func
from hash_func import md5
from io import BytesIO
import portalocker

def decrypt(dire, D, N, debug=False):
    try:
        if(os.path.isdir(dire)):
            if(dire[-1]!='/'):
                dire+='/'
            files=os.listdir(dire)
            for f in files:
                ret = decrypt(dire+f, D, N, debug)
                if ret != 0:
                    return ret
            return 0

        if (os.path.isfile(dire)):
            if(re.search('^.*?\.cipher$',dire)):
                ret, _ = decrypt_single_file(dire, D, N, debug)
                return ret
            print("ignore non-cipher file %s" % dire)
            return 0

        print("ignore file '%s', which is neither directory not file" % dire)
        return 0
    except:
        print(traceback.format_exc())
        return -1

        
def decrypt_single_file(filename, D, N, debug=False, memory_mode=False):
    print("D: %d, N: %d" % (D, N))
    try:
        flag=0
        print("Processing now: \""+filename+"\"")
        startTimeStamp=time.clock()
        src_rd=open(filename,'rb') #r stands for the file that is gonna be cyphered
        verify_chksum=False
        chksum_indication=src_rd.read(16)
        if chksum_indication == b'cchheecckkssuumm':
            verify_chksum=True
            chksum=src_rd.read(32)
            if len(chksum) < 32:
                print("checksum not correct")
                return -1, None
            chksum=chksum.decode('utf8')
        portalocker.lock(src_rd, portalocker.LOCK_EX) #lock the file
        size=os.path.getsize(filename)
    
        index=filename.rfind('.')
        decrypted_fname=filename[:index]  #get the name of the partly decrypted file
    

        r0_byte_read=1024*1024 # 1MB
        src_byte_read=r0_byte_read 
        if N > 65536:
            src_byte_read=int(r0_byte_read*3/2)
        if (not memory_mode) and os.path.isfile(decrypted_fname):
            decrypted_tmp_fname=''
            byte_processed=os.path.getsize(decrypted_fname)  #get the size of file which has already been processed
            decrypted_tmp_fname=decrypted_fname+'.tmp'  #temp file for copy and decrpyt
            decrypt_writer=open(decrypted_tmp_fname,'wb')  #write stream for temp file

            n=byte_processed/r0_byte_read
            r0=open(decrypted_fname,'rb')  #r0 stands for the read stream for partly decrpyted cypherfile
            while (1):
                line=r0.read(r0_byte_read)
                if not line or len(line) < r0_byte_read:
                    break
                src_rd.read(src_byte_read)
                decrypt_writer.write(line)
            r0.close()
            flag=1
        elif not memory_mode:
            decrypt_writer=open(decrypted_fname,'wb')
            flag=0
        else:
            decrypt_writer = BytesIO()
            flag=0

        while True:
            SpeedTimeS=time.clock()
            line=src_rd.read(src_byte_read)
            if not line:
                break

            b=list(line)
            if N > 65536:
                b_remain=len(b)%3
                assert(b_remain==0 or b_remain==1)
                a=[0]*(int(len(b)/3)*2+b_remain)
                a[-1]=b[-1]
                i=0
                j=0
                while True:
                    if j+2>=len(b):
                        break
                    first=int(b[j])
                    second=int(b[j+1])
                    third=int(b[j+2])
                    encoded=first*65536+second*256+third
                    ori=pow(encoded, D, N)
                    if ori > 65536:
                        raise Exception("FATAL ERROR: ori(%d) > 65536, maybe you are using a wrong key?" % ori)
                    a[i]=int(ori>>8)
                    a[i+1]=int(ori&255)
                    i+=2
                    j+=3
            else:
                a=b
                i=0
                while True:
                    if i+1>=len(a):
                        break
                    ori1=int(a[i])
                    ori2=int(a[i+1])
                    ori=ori1*256+ori2
                    if(ori<N):
                        ori=pow(ori, D, N)
                    ori1=ori>>8
                    ori2=ori&255
                    a[i]=int(ori1)
                    a[i+1]=int(ori2)
                    i+=2

            decrypt_writer.write(bytes(a))
            pos=src_rd.tell()
            SpeedTimeE=time.clock()
            SpeedTime=SpeedTimeE-SpeedTimeS
            time_remained=SpeedTime*(size-pos)/src_byte_read
            h=int(time_remained/3600)
            m=int(((int(time_remained))%3600)/60)
            s=(int(time_remained))%60
            print("has processed "+str(float(pos)/1000)+'kb, ' + "time remains %dh %dmin %ds" % (h,m,s))

        # Finished decryption            
        if memory_mode:
            decrypt_bytes = decrypt_writer.getvalue()
        decrypt_writer.close()
        portalocker.unlock(src_rd)
        assert(src_rd.tell() == size)
        src_rd.close()

        if flag:
            os.remove(decrypted_fname)
            os.rename(decrypted_tmp_fname, decrypted_fname)

        if memory_mode:
            if not decrypted_fname.endswith(".reverse"):
                return 0, decrypt_bytes

            decrypt_reader = BytesIO(decrypt_bytes)
            reversed_bytes = reverse_func(len(decrypt_bytes), decrypt_reader, memory_output=True)
            decrypt_reader.close()
            return 0, reversed_bytes

        if decrypted_fname.endswith(".reverse"):
            orig_fname=reverse_back(decrypted_fname)
        else:
            orig_fname=decrypted_fname

        if verify_chksum:
            orig_chksum=md5(orig_fname)
            if orig_chksum == chksum:
                print("\nChecksum OK, removing cipher file %s" % filename)
                os.remove(filename)
            else:
                print("Checksum Mismatch:")
                print("MD5(%s): %s" % (orig_fname, orig_chksum))
                print("Expect: %s" % chksum)
                if not debug:
                    print("Deleting corrupted file '%s'" % (orig_fname))
                    os.remove(orig_fname)
                else:
                    print("Renaming corrupted file '%s' to '%s'" % (orig_fname, orig_fname+".dbg"))
                    os.rename(orig_fname, orig_fname+".dbg")
                return -1, None
        else:
            os.remove(filename)
        endTimeStamp=time.clock()
        print("The file \""+filename+"\" has been decrypted successfully. Process totally %6.2f kb's document, cost %f seconds.\n"%(size/1000,endTimeStamp-startTimeStamp))
        return 0, None
    except:
        print(traceback.format_exc())
        decrypt_writer.close()
        portalocker.unlock(src_rd)
        print("Unlocked src_fd")
        src_rd.close()

        if(flag):
            os.remove(decrypted_fname)
            time.sleep(1)
            os.rename(decrypted_tmp_fname, decrypted_fname)
        return -1, None

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
    parser.add_argument('--debug', action='store_true', dest='debug', help='debug mode, will keep error files')
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
    decrypt(args.dir, args.D, args.N, args.debug)

