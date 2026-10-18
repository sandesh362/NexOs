"""Build the current static CLI as an uninstalled Linux Debian package."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
PACKAGE = "nexos-engine-foundation"


def main() -> None:
    if platform.system() != "Linux" or not shutil.which("dpkg-deb"):
        raise SystemExit("Build this package in Linux with dpkg-deb available")
    output = ROOT / "image" / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{PACKAGE}_{VERSION}_all.deb"
    hashes = {}
    temp_root = Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix="nexos-foundation-", dir=temp_root) as temporary:
        staging = Path(temporary).resolve()
        if not staging.is_relative_to(temp_root) or not staging.name.startswith("nexos-foundation-"):
            raise RuntimeError("Package staging cleanup target escaped the intended temporary directory")
        staging.chmod(0o755)
        control = staging / "DEBIAN"
        modules = staging / "usr/lib/nexos-foundation/nexos"
        executables = staging / "usr/bin"
        documentation = staging / "usr/share/doc" / PACKAGE
        for directory in (control, modules, executables, documentation):
            directory.mkdir(parents=True, exist_ok=True)
        for source in sorted((ROOT / "src/nexos").glob("*.py")):
            destination = modules / source.name
            destination.write_bytes(source.read_bytes())
            destination.chmod(0o644)
            hashes[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
        (control / "control").write_text(
            f"Package: {PACKAGE}\nVersion: {VERSION}\nArchitecture: all\n"
            "Maintainer: NEXOS Project\nSection: utils\nPriority: optional\nDepends: python3 (>= 3.12)\n"
            "Description: Static project diagnosis foundation for NEXOS\n"
            " Inspects explicitly granted manifests, creates reports and verifies evidence.\n"
            " This checkpoint does not contain the AI desktop or Linux tool sandbox.\n", encoding="utf-8")
        launcher = executables / "nexos-foundation"
        launcher.write_text(
            "#!/usr/bin/python3\nimport sys\nfrom pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib/nexos-foundation'))\n"
            "from nexos.cli import main\nraise SystemExit(main())\n", encoding="utf-8")
        launcher.chmod(0o755)
        (documentation / "README").write_text(
            "NEXOS foundation 0.1.0\nStatic manifest inspection and verified reports.\n"
            "Local source packaging checkpoint; full agentic runtime and ISO integration follow.\n"
            "No public redistribution license has been selected for project source.\n", encoding="utf-8")
        environment = os.environ.copy()
        environment.setdefault("SOURCE_DATE_EPOCH", "1792368000")
        subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(staging), str(target)],
                       check=True, env=environment)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {"package": PACKAGE, "version": VERSION, "artifact": target.name,
                "sha256": digest, "source_hashes": hashes,
                "scope": "Static manifest diagnosis CLI; no desktop, model or OS sandbox"}
    target.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    target.with_suffix(".sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    print(json.dumps({"artifact": str(target), "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
