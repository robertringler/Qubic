#!/usr/bin/env python3
"""Comprehensive repository validation harness for QuASIM Stage I."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TaskResult:
    name: str
    status: str
    detail: str = ""

    def as_row(self) -> str:
        return f"{self.status.upper():<8} {self.name} - {self.detail}".rstrip()


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(command: Sequence[str], cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def terraform_targets() -> Iterable[Path]:
    for directory in (
        ROOT / "infra" / "terraform" / "eks",
        ROOT / "infra" / "terraform" / "modules" / "vpc",
    ):
        if directory.is_dir():
            yield directory


def validate_terraform(results: List[TaskResult]) -> None:
    if not command_available("terraform"):
        results.append(TaskResult("Terraform validation", "skipped", "terraform CLI not available"))
        return

    for target in terraform_targets():
        init = run_command(["terraform", "init", "-backend=false"], cwd=target)
        if init.returncode != 0:
            results.append(
                TaskResult(
                    f"Terraform init ({target.relative_to(ROOT)})",
                    "failed",
                    init.stderr.strip() or init.stdout.strip(),
                )
            )
            continue
        results.append(
            TaskResult(
                f"Terraform init ({target.relative_to(ROOT)})",
                "passed",
                "backend disabled",
            )
        )

        validate = run_command(["terraform", "validate"], cwd=target)
        if validate.returncode != 0:
            results.append(
                TaskResult(
                    f"Terraform validate ({target.relative_to(ROOT)})",
                    "failed",
                    validate.stderr.strip() or validate.stdout.strip(),
                )
            )
        else:
            results.append(
                TaskResult(
                    f"Terraform validate ({target.relative_to(ROOT)})",
                    "passed",
                    "configuration syntax OK",
                )
            )


def load_yaml_documents(path: Path) -> None:
    import yaml  # type: ignore

    with path.open("r", encoding="utf-8") as handle:
        list(yaml.safe_load_all(handle))


def validate_yaml(results: List[TaskResult]) -> None:
    yaml_files = sorted(ROOT.glob("infra/**/*.yaml"))
    if not yaml_files:
        results.append(TaskResult("YAML discovery", "skipped", "no YAML files found"))
        return

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        results.append(TaskResult("YAML validation", "skipped", "PyYAML module not installed"))
        return

    for path in yaml_files:
        try:
            load_yaml_documents(path)
        except Exception as exc:  # pragma: no cover - diagnostic detail
            results.append(TaskResult(f"YAML parse ({path.relative_to(ROOT)})", "failed", str(exc)))
        else:
            results.append(TaskResult(f"YAML parse ({path.relative_to(ROOT)})", "passed", "valid syntax"))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repository validation checks.")
    parser.add_argument("--summary", action="store_true", help="Only print the summary table.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    _ = parse_args(argv)
    results: List[TaskResult] = []

    validate_terraform(results)
    validate_yaml(results)

    failed = False
    print("QuASIM Stage I validation results:\n")
    for record in results:
        print(record.as_row())
        if record.status.lower() == "failed":
            failed = True

    if failed:
        print("\nOne or more checks failed.")
        return 1

    print("\nAll executable checks completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
