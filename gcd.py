
def gcd(p, q):
    # Create the gcd of two positive integers.
    while q != 0:
        p, q = q, p % q
    return p


if __name__ == "__main__":
    import sys

    print("gcd: %d" % gcd(int(sys.argv[1]), int(sys.argv[2])))
