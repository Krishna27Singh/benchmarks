import sys


def fib_recursive(n):
    return n if n <= 1 else fib_recursive(n - 1) + fib_recursive(n - 2)


def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


mode, n = sys.argv[1], int(sys.argv[2])
if mode == "recursive":
    print(fib_recursive(n))
else:
    print(sum(fib_iter(30 + k % 10) for k in range(n)))