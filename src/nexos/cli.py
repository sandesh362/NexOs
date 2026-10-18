from __future__ import annotations

import argparse
import json
import platform
import shutil
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .diagnosis import diagnose


def readiness(workspace: str | Path) -> dict:
    location = Path(workspace).resolve(strict=True)
    programs = {name: shutil.which(name) for name in ("cubic", "mksquashfs", "xorriso", "dpkg-deb", "bwrap")}
    free = shutil.disk_usage(location).free
    linux = platform.system() == "Linux"
    storage = free >= 100 * 1024 ** 3
    return {"version": __version__, "platform": platform.system(), "python": platform.python_version(),
            "workspace": str(location), "free_gib": round(free / 1024 ** 3, 1),
            "linux_builder": linux, "build_tools": programs,
            "suggested_image_workspace_gib": 100, "storage_budget_met": storage,
            "iso_environment_ready": linux and all(programs.values()) and storage,
            "runtime_packages_ready": False,
            "note": "Environment inspection only; image assembly also requires qualified runtime packages and a verified Ubuntu base."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nexos", description="NEXOS deterministic foundation; no model or OS sandbox is implemented yet")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Inspect the current ISO build environment without changing it")
    doctor.add_argument("--workspace", default=".")
    doctor.add_argument("--require-iso", action="store_true", help="Return a failing status when the image build environment is not ready")
    diagnostic = commands.add_parser("diagnose", help="Inspect registered static manifests and create a verified report")
    diagnostic.add_argument("--project", required=True)
    diagnostic.add_argument("--output", required=True)
    diagnostic.add_argument("--state", default=".nexos/state.sqlite3")
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "doctor":
            result = readiness(arguments.workspace)
            print(json.dumps(result, indent=2))
            return 2 if arguments.require_iso and not result["iso_environment_ready"] else 0
        result = diagnose(arguments.project, arguments.output, arguments.state)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, sqlite3.Error) as error:
        print(json.dumps({"status": "FAILED", "error_type": type(error).__name__, "reason": str(error)}), file=sys.stderr)
        return 1
