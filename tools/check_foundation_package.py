"""Smoke test an extracted foundation package without installing it."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "image/artifacts/nexos-engine-foundation_0.1.0_all.deb"


def main():
    manifest = json.loads(PACKAGE.with_suffix(".manifest.json").read_text())
    if hashlib.sha256(PACKAGE.read_bytes()).hexdigest() != manifest["sha256"]:
        raise RuntimeError("Package checksum differs from its manifest")
    temp_root = Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix="nexos-package-check-", dir=temp_root) as temporary:
        destination = Path(temporary).resolve()
        if not destination.is_relative_to(temp_root) or not destination.name.startswith("nexos-package-check-"):
            raise RuntimeError("Package check cleanup target escaped its temporary directory")
        subprocess.run(["dpkg-deb", "--extract", str(PACKAGE), str(destination)], check=True)
        launcher = destination / "usr/bin/nexos-foundation"
        version = subprocess.check_output([sys.executable, str(launcher), "--version"], text=True).strip()
        if version != "0.1.0":
            raise RuntimeError("Unexpected packaged CLI version")
        output = subprocess.check_output([
            sys.executable, str(launcher), "diagnose", "--project", str(ROOT / "examples/demo-project"),
            "--output", str(destination / "reports"), "--state", str(destination / "state.sqlite3")
        ], text=True)
        result = json.loads(output)
        if result["status"] != "SUCCEEDED" or not all(result["verification"].values()):
            raise RuntimeError("Packaged diagnosis did not verify")
    print(json.dumps({"package": PACKAGE.name, "checksum_matches": True,
                      "packaged_version": version, "packaged_diagnosis_verified": True,
                      "installed_on_host": False}, indent=2))


if __name__ == "__main__":
    main()
