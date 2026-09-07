"""Reproducible measurements on one CI runner; does not edit application sources."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

out = Path("reports")
out.mkdir(exist_ok=True)
results = []
def timed(label, command):
    start = time.perf_counter()
    with (out / (label + ".log")).open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    seconds = round(time.perf_counter() - start, 3)
    results.append({"measurement": label, "seconds": seconds})
    print(f"{label}: {seconds}s", flush=True)

def size(tag):
    return int(subprocess.check_output(["docker", "image", "inspect", tag, "--format", "{{.Size}}"], text=True))

with tempfile.TemporaryDirectory() as tmp:
    for layout in ("bad", "good"):
        context = Path(tmp) / layout
        shutil.copytree("backend", context)
        header = "FROM python:3.10-alpine\nENV PYTHONUNBUFFERED=1\nWORKDIR /code\n"
        install = "RUN pip install -r requirements.txt\n"
        layers = "COPY . .\n" + install if layout == "bad" else "COPY requirements.txt .\n" + install + "COPY . .\n"
        (context / "Dockerfile").write_text(header + layers + 'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]\n')
        for state in ("initial", "changed"):
            if state == "changed":
                with (context / "manage.py").open("a") as source:
                    source.write("\n# Harmless source-only cache benchmark change\n")
            flags = ["--no-cache"] if state == "initial" else []
            timed(f"docker-{layout}-{state}", ["docker", "build", "--progress=plain", *flags, "-t", f"taski-benchmark-{layout}", str(context)])
    timed("backend-multi-stage", ["docker", "build", "--progress=plain", "-t", "taski-benchmark-multi", "backend"])
    # Same final Dockerfile built again shows Docker's unmodified layer reuse.
    timed("backend-multi-stage-warm", ["docker", "build", "--progress=plain", "-t", "taski-benchmark-multi", "backend"])

sizes = {"backend-single-stage": size("taski-benchmark-good"), "backend-multi-stage": size("taski-benchmark-multi")}
(out / "measurements.json").write_text(json.dumps({"timings": results, "image_bytes": sizes}, indent=2) + "\n")
lines = ["# Taski build measurements", "", "One GitHub Actions runner. Wall-clock build times include Docker overhead.", "", "| Measurement | Seconds |", "|---|---:|"]
lines += [f"| {row['measurement']} | {row['seconds']} |" for row in results]
lines += ["", "| Backend image | MiB |", "|---|---:|"]
lines += [f"| {name} | {value / 1024**2:.2f} |" for name, value in sizes.items()]
lines += ["", "The single-stage baseline follows the lesson and retains pip download cache. The final image uses multi-stage plus --no-cache-dir; size savings cannot be attributed to multi-stage alone.", "Network and runner noise affect timing; these are measured results, not guaranteed speedups."]
report = "\n".join(lines) + "\n"
(out / "measurements.md").write_text(report)
print(report)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
        summary.write(report)
