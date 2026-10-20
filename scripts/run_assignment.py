"""Reproduce the complete numerical assignment and its submission package."""

import argparse
from pathlib import Path
import subprocess
import sys


def main(workers=3):
    root = Path(__file__).resolve().parent
    stages = [
        ["run_discretization.py", "--stage", "independent", "--workers", str(workers)],
        ["run_discretization.py", "--stage", "qualify", "--outer", "96", "--inner", "128", "--workers", str(workers)],
        ["run_discretization.py", "--stage", "worst-case", "--workers", str(workers)],
        ["run_discretization.py", "--stage", "support", "--outer", "96", "--inner", "128", "--workers", str(workers)],
        ["finalize_discretization.py"], ["plot_discretization.py"],
        ["run_parameter_studies.py", "--workers", str(workers)], ["run_analytical.py"], ["plot_studies.py"],
        ["build_submission.py"],
    ]
    for command in stages:
        print("Running "+" ".join(command), flush=True)
        subprocess.run([sys.executable, *command], cwd=root, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    main(parser.parse_args().workers)
