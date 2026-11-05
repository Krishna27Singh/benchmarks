# Fibonacci

CPU bound benchmark for function call overhead, integer loops and `range` iteration.

| Case | Workload | Expected output |
|---|---|---|
| `recursive_35` | naive recursive fib(35) | `9227465` |
| `recursive_40` | naive recursive fib(40) | `102334155` |
| `iterative_1m` | sum of fib(30 + k % 10) for k in 0..1,000,000 | `16423387200000` |

`recursive_*` measures call overhead. `iterative_1m` runs about 34.5 million loop iterations of
integer addition. It has two Arx variants:

- `arx-while`: `while` loops only.
- `arx-range`: `for ... in range(...)`. `range` currently allocates a list on every call.

## Implementations

| Label | Source | Build |
|---|---|---|
| `arx` / `arx-while` / `arx-range` | `arx/*.x` | `arx <file> --output-file <bin>` |
| `c-O0`, `c-O2` | `c/fib.c` | `clang -O0` / `clang -O2` |
| `python` | `python/fib.py` | run with the harness's Python |

C and Python read the case arguments from the command line. Arx programs have
the inputs written into the source.

## Reproduce

Requirements: Python >= 3.11, `hyperfine`, `clang` and `arx` on `PATH`. See the
[top level README](../../README.md#requirements). From the repository root:

```bash
python3 harness/bench.py list                       # shows the three cases
python3 harness/bench.py check fibonacci            # compile and verify every output
python3 harness/bench.py run fibonacci              # verify, then time 
python3 harness/bench.py report                     # markdown tables for the latest run
python3 harness/bench.py report results/<run-dir>   # tables for a specific run
```

Close other applications first and, on a laptop, use mains power. If a `stddev` is above about 5%
of its median, rerun. Use `run fibonacci --quick` only as a smoke test; its output goes to
`build/quick-results/` and must not be published.

To contribute results from another machine, run the commands above and open a PR adding the new
directory under `results/`.

## Method

- Every implementation runs once before timing and must print the expected output. A mismatch
  aborts the run. This first run also absorbs the macOS first launch check on freshly built binaries.
- Compiled executables are timed with hyperfine (`-N`, no shell) after warm up runs; the number
  of runs is set per case in `benchmark.toml`. Compile time is excluded.
- The tables show median, min and standard deviation of wall clock time, peak memory as reported by
  hyperfine, and a ratio to the fastest implementation in that case.

## Caveats

- Arx integer arithmetic is overflow checked, C is unchecked and Python integers are unbounded.
- Arx inputs are compile time constants. The C and Python inputs come from the command line, so the
  C compiler cannot fold the work away.
- Timings include process start up. For `python` this is a few tens of milliseconds, which is
  negligible for these case sizes.
- One machine, one run configuration. Compare ratios, not absolute times, across machines.
- The Arx compiler's own optimization level has not been documented yet, so the `c-O0`/`c-O2`
  columns show where Arx lands relative to unoptimized and optimized C, not why.

## Results

Run `python3 harness/bench.py run fibonacci` on:

> Apple M1 | macOS 27.0.1 (arm64) | Arx 1.27.0 (`5ff7e9db`) | Apple clang 21.0.0 | hyperfine 2.0.0 | Python 3.14.10

Raw data: [`results/<run-dir>/`](../../results/).

<!-- paste the three tables from `python3 harness/bench.py report` here -->

### Observations

**iterative_1m**

| implementation | median (s) | min (s) | stddev (s) | memory (MiB) | vs fastest |
|---|---|---|---|---|---|
| arx-while | 0.1223 | 0.1209 | 0.0015 | 1.6 | 5.2x |
| arx-range | 1.3164 | 1.3073 | 0.0433 | 1.7 | 56.0x |
| c-O0 | 0.0861 | 0.0858 | 0.0007 | 1.5 | 3.7x |
| c-O2 | 0.0235 | 0.0229 | 0.0004 | 1.5 | 1.0x |
| python | 0.9460 | 0.9450 | 0.0146 | 9.6 | 40.2x |

**recursive_35**

| implementation | median (s) | min (s) | stddev (s) | memory (MiB) | vs fastest |
|---|---|---|---|---|---|
| arx | 0.0937 | 0.0930 | 0.0006 | 1.6 | 1.8x |
| c-O0 | 0.0853 | 0.0847 | 0.0018 | 1.5 | 1.7x |
| c-O2 | 0.0507 | 0.0497 | 0.0004 | 1.5 | 1.0x |
| python | 1.1426 | 1.1387 | 0.0280 | 9.6 | 22.5x |

**recursive_40**

| implementation | median (s) | min (s) | stddev (s) | memory (MiB) | vs fastest |
|---|---|---|---|---|---|
| arx | 0.9929 | 0.9905 | 0.0187 | 1.6 | 1.9x |
| c-O0 | 0.8980 | 0.8976 | 0.0218 | 1.5 | 1.8x |
| c-O2 | 0.5096 | 0.5085 | 0.0009 | 1.5 | 1.0x |
| python | 12.6159 | 12.5125 | 0.0849 | 9.7 | 24.8x |

- **Recursion:** Arx is within about 1.1x of `c-O0` and about 1.9x slower than `c-O2` on
  `recursive_35` and `recursive_40`. It is about 12x faster than CPython (12.7x on fib(40)).
- **`arx-while`:** about 1.4x slower than `c-O0`, 5.2x slower than `c-O2` and 7.7x faster than CPython.
- **`arx-range`:** 10.8x slower than `arx-while` and 1.4x slower than CPython, because `range` allocates a list per call.
- **Memory:** peak memory is about 1.5-1.7 MiB for Arx and C and about 9.6 MiB for CPython.