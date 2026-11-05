# Arx benchmarks

Reproducible benchmarks for the [Arx](https://github.com/arxlang/arx) compiler. Each suite
implements the same workload in Arx, C (clang `-O0` and `-O2`) and CPython, verifies that all
implementations print the same output, and times the compiled executables with
[hyperfine](https://github.com/sharkdp/hyperfine).


## Suites

| Suite | Measures | Results |
|---|---|---|
| [`fibonacci`](suites/fibonacci/README.md) | function calls, integer loops, `range` iteration | [`results/`](results/) |

## Quick start

```bash
python3 harness/bench.py list
python3 harness/bench.py check fibonacci     # build and verify outputs
python3 harness/bench.py run fibonacci       # verify, then time
python3 harness/bench.py report              # markdown tables from the latest run
```

## Requirements

- Python >= 3.11 (the harness uses `tomllib`)
- [hyperfine](https://github.com/sharkdp/hyperfine) (tested with 2.0.0)
- `clang` and `arx` on `PATH`
- Optional: `ARX_REPO=/path/to/arx` records the Arx git commit in the results

On macOS, put Apple's `/usr/bin/clang` first on `PATH`. In testing, a conda-provided clang failed
to link Arx output (`ld: -lto_library library filename must be 'libLTO.dylib'`). The harness warns
if it finds one. Tested on macOS arm64 only; 

## Layout

| Path | Purpose |
|---|---|
| `suites/<name>/benchmark.toml` | Manifest: cases, arguments, expected output, run counts |
| `suites/<name>/{arx,c,python}/` | One implementation per language |
| `suites/<name>/README.md` | What the suite measures, caveats, results |
| `harness/bench.py` | Generic runner with no benchmark specific code |
| `results/<date>_<os>-<arch>_arx-<version>/` | Raw hyperfine JSON and `environment.json` |
| `build/` | Compiled binaries and quick runs (git ignored) |

## Method

1. **Build.** Arx programs are compiled with `arx`; C with `clang -O0` and `clang -O2`.
   Compile time is not part of the measurement.
2. **Verify.** Each implementation runs once and must print the case's `expected` output
   with exit code 0. Any mismatch aborts the run.
3. **Time.** hyperfine runs each executable directly (`-N`, no shell) after warm up runs.
4. **Record.** Raw JSON and `environment.json` are written to `results/`.

### Why these baselines

- **C with clang `-O0` / `-O2`:** Arx lowers to LLVM IR and links with clang, so C built by the same
  toolchain is the closest native reference. `-O0` is the no optimization floor and `-O2` is a
  normal release build.
- **CPython:** Arx has Python like syntax. Large gaps are expected because it is an interpreter.

## Results and reproducibility

- **Outputs** are deterministic and checked on every run.
- **Timings** depend on CPU, thermals, OS and background load, and are not reproducible across
  machines. Compare ratios, not absolute times, and compare runs only when their
  `environment.json` files are comparable.
- Every run directory contains `environment.json`. The tables in the
  suite READMEs are generated from the JSON next to it.

## Limitations

hyperfine measures whole process wall clock time. As a result:

- Process start up is included, and individual phases cannot be timed inside a program.
- There are no hardware counters (instructions, cache or branch misses).
- There is no CPU pinning or frequency control.
- Statistics are descriptive (median, min, stddev); there is no regression detection across versions.

## Adding a benchmark

Create `suites/<name>/` with a manifest and sources. The harness discovers it automatically.

```toml
name = "mybench"
description = "What it measures"

[references]                    # optional; each receives the case's `args`
c = "c/mybench.c"
python = "python/mybench.py"

[[case]]
id = "small"
args = ["100"]                  # passed to the C and Python references
expected = "42"                 # exact stdout, trimmed
runs = 10
warmup = 2
[case.arx]                      # label = source (Arx programs take no arguments)
arx = "arx/small.x"
```


## License

BSD-3-Clause, see [LICENSE](LICENSE).