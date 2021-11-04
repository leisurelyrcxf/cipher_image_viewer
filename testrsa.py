import rsa
def main():
    (publicKey,privateKey)=rsa.newkeys(512)
    print type(privateKey)
    print '\n'
    
    message=open('test.txt','r').read()
    w=open('cipher.txt','w')
    w1=open('privatekey','w')
    print >>w1, privateKey
    pos=0
    cipher=""
    while 1:
        if pos+50<len(message):
            
            cipher+=rsa.encrypt(message[pos:pos+50],publicKey)+"!@#$%^&*"
            pos+=50
        else:
            
            cipher+=rsa.encrypt(message[pos:],publicKey)
            w.write(cipher)
            w.close()
            break
    

def main1():
    cipher=open('cipher.txt','r').read()
    w=open('origine.txt','w')
    privateKey=rsa.key.PrivateKey(8665099110430052193548187260675089417444078100960306533319508423191291639191737505077172203902215933209429272590153251856881903875635843498099374433005011, 65537, 7329443965800844459608217660184683184399842371892741393023283785336668625796939850306807341273315081379866161137201502666466551320095510503852011584608473, 5226660440741265339677993215265165729594330229343965461482179496231205915063556701, 1657865325033652672153837122819963459416457195097251792889858205771171311)
    pos=0
    origine=""
    while 1:
        pos=cipher.find("!@#$%^&*")
        if pos!=-1:
            origine+=rsa.decrypt(cipher[:pos],privateKey)
            cipher=cipher[pos+8:]
        else:
            origine+=rsa.decrypt(cipher,privateKey)
            w.write(origine)
            w.close()
            break    
if __name__=='__main__':
    main()
