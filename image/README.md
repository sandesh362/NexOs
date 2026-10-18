# NEXOS image preparation

This directory begins the distribution build inputs. It does not yet contain
a qualified image recipe or a bootable ISO.

The first application artifact is `nexos-engine-foundation`, a small Debian
package containing the static diagnosis CLI. It intentionally has no service,
desktop assistant, model or process execution adapter yet. It is a packaging
checkpoint; the release image requires the later integrated packages.

## Inputs now present

- `package-lists/runtime-base.list` lists additional Ubuntu runtime packages.
- `package-lists/builder-tools.list` lists Linux image builder dependencies.
- `../tools/build_foundation_deb.py` packages the current source on Linux.
- `../docs/build/BUILD_WORKFLOW.md` defines milestones and release gates.

From the repository root in a Python 3.12 Ubuntu environment with `dpkg-deb`:

```bash
python3 tools/build_foundation_deb.py
```

The builder writes the foundation `.deb` and its checksum and source manifest
under `image/artifacts/`. It builds without installing the package or modifying
system services. Those generated outputs are excluded from version control.

## Before assembling an ISO

Select and verify an exact Ubuntu 24.04 Desktop base image. Prepare an Ubuntu
builder with the documented Cubic release and required tools, and record all
versions. The existing WSL Ubuntu can run tests and Debian packaging; the Cubic
GUI and any image assembly under WSL require their own qualification. Keep the
first full desktop image construction on a tested Ubuntu desktop builder if
those requirements are not met.

Add the working engine, native desktop, session integration and inference
runtime through their packages. Capture customization as package lists,
overlays and scripts. Keep personal home directories, tokens and active browser
sessions out of the image. A verified live boot must be followed by installation
to a fresh VM disk and reboot after removing the ISO.
