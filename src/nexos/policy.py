"""Explicit filesystem capabilities for the static diagnosis prototype.

This is an application boundary, not a Linux process sandbox. The prototype
does not launch project code or subprocess tools. Host account compromise
and concurrent hostile filesystem mutation require later OS level controls.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path


class PermissionDenied(ValueError):
    pass


def check_no_links(path: Path) -> None:
    for component in (path, *path.parents):
        is_junction = getattr(component, "is_junction", lambda: False)
        if component.is_symlink() or is_junction():
            raise PermissionDenied("Symbolic links and junctions are outside prototype capabilities")


def absolute_path(value: str | Path) -> Path:
    path = Path(os.path.abspath(value))
    check_no_links(path)
    return path


def read_regular_file(path: Path, maximum: int) -> bytes:
    check_no_links(path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        details = os.fstat(stream.fileno())
        if not stat.S_ISREG(details.st_mode):
            raise PermissionDenied("Only regular files can be read")
        if details.st_size > maximum:
            raise PermissionDenied(f"File exceeds the {maximum} byte read limit")
        result = stream.read(maximum + 1)
        if len(result) > maximum:
            raise PermissionDenied("File grew beyond the read limit")
        return result


class FileCapabilities:
    MANIFESTS = frozenset({"pyproject.toml", "requirements.txt", "package.json"})

    def __init__(self, project: str | Path, output: str | Path):
        self.project = absolute_path(project)
        self.output = absolute_path(output)
        if not self.project.is_dir():
            raise ValueError("The granted project directory does not exist")

    def read_manifest(self, name: str) -> bytes:
        if name not in self.MANIFESTS:
            raise PermissionDenied("This tool can read only registered project manifests")
        return read_regular_file(self.project / name, 128 * 1024)

    def manifest_exists(self, name: str) -> bool:
        if name not in self.MANIFESTS:
            raise PermissionDenied("Unknown manifest")
        candidate = self.project / name
        check_no_links(candidate)
        if candidate.exists() and not candidate.is_file():
            raise PermissionDenied("A manifest must be a regular file")
        return candidate.exists()

    def report_path(self, name: str) -> Path:
        if not name or name in {".", ".."} or Path(name).name != name or any(char in name for char in ("/", "\\", ":")):
            raise PermissionDenied("Reports need a simple filename inside the granted output directory")
        result = self.output / name
        check_no_links(result)
        return result

    def write_report(self, name: str, content: bytes) -> Path:
        if len(content) > 512 * 1024:
            raise PermissionDenied("Report exceeds the write limit")
        target = self.report_path(name)
        self.output.mkdir(parents=True, exist_ok=True)
        check_no_links(self.output)
        # Exclusive creation protects existing files from accidental overwrite.
        with target.open("xb") as stream:
            stream.write(content)
        return target

    def read_report(self, name: str) -> bytes:
        return read_regular_file(self.report_path(name), 512 * 1024)
