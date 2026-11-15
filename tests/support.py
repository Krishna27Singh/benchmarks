import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))
import bench  # noqa: E402


def write_hyperfine_1(path, rows):
    payload = {"results": []}
    for row in rows:
        times = row.get("times", [row["median"]])
        memory = row.get("memory_usage_byte")
        result = {
            "command": row["command"],
            "mean": row.get("mean", row["median"]),
            "stddev": row.get("stddev", 0.0),
            "median": row["median"],
            "min": row["min"],
            "max": row.get("max", max(times)),
            "user": row.get("user", row.get("mean", row["median"])),
            "system": row.get("system", 0.0),
            "times": times,
            "exit_codes": row.get("exit_codes", [0] * len(times)),
        }
        if memory is not None:
            result["memory_usage_byte"] = memory if isinstance(memory, list) else [memory]
        payload["results"].append(result)
    path.write_text(json.dumps(payload) + "\n")


def write_hyperfine_2(path, rows):
    payload = {
        "schema_version": 2,
        "metadata": {
            "hyperfine_version": "2.0.0",
            "start_time": "2026-11-14T00:00:00Z",
            "platform": {"os": "Darwin", "architecture": "arm64"},
        },
        "primary_metric": "time_wall_clock",
        "results": [],
    }
    for row in rows:
        measurements = row.get("measurements")
        if measurements is None:
            measurements = [{"time_wall_clock": row["median"]} for _ in range(3)]
            if "memory" in row:
                for measurement in measurements:
                    measurement["memory_peak_resident"] = row["memory"]
        result = {
            "command": row["command"],
            "name": row["name"],
            "measurements": measurements,
            "summary": {
                "time_wall_clock": {
                    "mean": row.get("mean", row["median"]),
                    "median": row["median"],
                    "min": row["min"],
                    "stddev": row.get("stddev", 0.0),
                    "max": row.get("max", row["median"]),
                }
            },
        }
        if "memory" in row:
            result["summary"]["memory_peak_resident"] = {
                "mean": row["memory"],
                "stddev": 0.0,
                "median": row["memory"],
                "min": row["memory"],
                "max": row["memory"],
            }
        payload["results"].append(result)
    path.write_text(json.dumps(payload) + "\n")


def make_run(root, version, case_rows, baseline_rows, memory=True):
    run = root / f"2026-11-14T000000Z_{version}"
    run.mkdir()
    suite = run / "fake"
    suite.mkdir()
    environment = {
        "timestamp_utc": "2026-11-14T000000Z",
        "date": "2026-11-14",
        "arx": "1.28.0",
        "arx_commit": "test",
        "clang": "test",
        "hyperfine": version,
        "python": "test",
        "os": "test",
        "cpu": "test",
    }
    (run / "environment.json").write_text(json.dumps(environment) + "\n")
    (run / "complete.json").write_text(json.dumps({
        "schema_version": 1,
        "status": "complete",
        "timestamp_utc": environment["timestamp_utc"],
    }) + "\n")
    if version == "1.x":
        write_hyperfine_1(run / "_baseline.json", baseline_rows)
        write_hyperfine_1(suite / "case.json", case_rows)
    else:
        write_hyperfine_2(run / "_baseline.json", baseline_rows)
        write_hyperfine_2(suite / "case.json", case_rows)
    if not memory:
        for path in (run / "_baseline.json", suite / "case.json"):
            data = json.loads(path.read_text())
            for result in data["results"]:
                result.pop("memory_usage_byte", None)
                result.get("summary", {}).pop("memory_peak_resident", None)
            path.write_text(json.dumps(data) + "\n")
    return run


def make_fake_suite(root, expected="42"):
    suite = root / "fake"
    (suite / "python").mkdir(parents=True)
    (suite / "benchmark.toml").write_text(
        'name = "fake"\n'
        'description = "Python-only smoke suite"\n'
        "\n"
        "[references]\n"
        'python = "python/fib.py"\n'
        "\n"
        "[[case]]\n"
        'id = "small"\n'
        'args = []\n'
        'input = "7"\n'
        f'expected = "{expected}"\n'
        "runs = 1\n"
        "warmup = 1\n"
    )
    (suite / "python" / "fib.py").write_text(
        "from pathlib import Path\n"
        'print("42" if Path("input.txt").read_text().strip() == "7" else "0")\n'
    )
    return suite
