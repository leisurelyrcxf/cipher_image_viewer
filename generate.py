import math
import os

def gcd(p,q):
    # Create the gcd of two positive integers.
    while q != 0:
        p, q = q, p%q
    return p

def is_coprime(x, y):
    return gcd(x, y) == 1

def is_prime(n):
    for i in range(2, int(math.sqrt(n))+1):
       if n % i == 0:
            return False 
    return True

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('-p', type=int, dest='p', help='p', default=251)
    parser.add_argument('-q', type=int, dest='q', help='q', default=131)
    args=parser.parse_args()
    p=args.p
    q=args.q
    if not is_prime(p):
        print("%d is not a prime" % p)
        exit(1)
    if not is_prime(q):
        print("%d is not a prime" % q)
        exit(1)
    N=p*q
    if N > 65536:
        print("must guarantee p*q <= 65536, got %d" % N)
        exit(1)
    r=(p-1)*(q-1)
    print("p: %d, q: %d, r: %d" % (p, q, r))
    coprimes=[]
    for i in range(2, r):
        if is_coprime(i, r):
            coprimes.append(i)
    import secrets
    e=secrets.choice(coprimes)
    for d in range(2, r+1):
        if d*e%r == 1:
            break
    if d*e%r != 1:
        print("fatal error, can't find d for (e(%d), r(%d)) % (e, r)")
        exit(1)
    print("------------------------------------------------------------")
    print("Keys generated")
    print("e: %d , d: %d , N: %d" % (e, d, N))
    
            
       
