#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static long long fib_rec(long long n) {
    return n <= 1 ? n : fib_rec(n - 1) + fib_rec(n - 2);
}

static long long fib_iter(long long n) {
    long long a = 0, b = 1;
    for (long long i = 0; i < n; i++) {
        long long t = a;
        a = b;
        b = t + b;
    }
    return a;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: fib recursive|iterative N\n");
        return 2;
    }
    long long n = atoll(argv[2]);
    if (strcmp(argv[1], "recursive") == 0) {
        printf("%lld\n", fib_rec(n));
        return 0;
    }
    long long total = 0;
    for (long long k = 0; k < n; k++) total += fib_iter(30 + k % 10);
    printf("%lld\n", total);
    return 0;
}