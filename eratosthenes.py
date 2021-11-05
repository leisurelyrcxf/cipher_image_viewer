
def naive(n):
    def is_prime(n):
        for i in range(2, int(n ** 0.5)+1):
           if n % i == 0:
                return False 
        return True
    return [x for x in range(2, n+1) if is_prime(x)] 


def eratosthenes(n):
    IsPrime = [True] * (n+1)
    for i in range(2, int(n ** 0.5) + 1):
        if IsPrime[i]:
            for j in range(i * i, n + 1, i):
                IsPrime[j] = False
    return [x for x in range(2, n+1) if IsPrime[x]]

if __name__ == "__main__":
    import sys
    n=int(sys.argv[1])
    primes=eratosthenes(n)
    print(primes)
    print("Number: %d" % len(primes))
    naive_primes=naive(n)
    assert primes == naive_primes
