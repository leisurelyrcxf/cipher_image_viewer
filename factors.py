from typing import List


def trial_division(n: int) -> List[int]:
    a = []
    while n % 2 == 0:
        a.append(2)
        n //= 2
    f = 3
    while f * f <= n:
        if n % f == 0:
            a.append(f)
            n //= f
        else:
            f += 2
    if n != 1: a.append(n)
    # Only odd number is possible
    return a


if __name__ == "__main__":
    import sys

    factors = trial_division(int(sys.argv[1]))
    print(factors)
