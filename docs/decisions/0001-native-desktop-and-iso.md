# Native desktop and bootable ISO delivery

Date: 18 October 2026

Status: adopted for the implementation blueprint

## Context

The intended product is a bootable Linux distribution with integrated AI automation, distributed in the same broad forms as an ISO installer or a preconfigured virtual machine. The primary interface must be a native desktop experience. The earlier architecture proposed a browser served React interface and treated custom ISO packaging as optional.

## Decision

1. Retain Ubuntu 24.04 LTS as the base, including its existing kernel, desktop and package infrastructure.
2. Implement the assistant in Qt 6 with PySide6 and Qt Quick/QML.
3. Run the Python engine as a systemd user service. Use a private Unix domain socket for the desktop and CLI protocol.
4. Run Ollama inside the guest as a separate inference service. NEXOS implements agent orchestration and authority; Ollama supplies inference.
5. Deliver a customized bootable ISO as a required release artifact. Build native Debian packages first and integrate those same packages into the image.
6. Begin image construction with Cubic and version controlled customization inputs on an Ubuntu builder. Validate both live boot and installed systems. Automate additional assembly steps after the prototype demonstrates the installer path.
7. Produce a Core image with model setup and an offline demo variant with a tested model when capacity and redistribution terms permit. An optional prebuilt VM is derived from a sanitized installation.
8. Target a declared x86_64 VMware Workstation UEFI configuration first. Publish broader support only after tests.

## Consequences

React, a browser served UI and FastAPI are no longer core runtime dependencies. The interface and engine remain separate processes with typed messages. The inference service may still use its internal loopback HTTP API.

The required ISO adds image customization, installer retention, guest tools, first run state, model availability, credential sanitation, checksums and clean VM boot tests. A live session and installed virtual disk have different persistence behavior and must be tested separately.

The current 60 GB of free disk space supports a constrained development environment. It is not a comfortable allowance for simultaneous VM and full image builds. Plan a separate builder or roughly 100 to 120 GB of free build workspace as an estimate to validate.

This changes distribution and presentation choices while preserving the earlier permission broker, typed tools, independent verification, memory provenance and benchmark design. It does not introduce a new kernel or promise unrestricted system automation.

## Documentation precedence

The [README](../../README.md) and this decision take precedence over the corresponding UI, local API, ISO scope and image build capacity statements in the earlier [architecture report](../NEXOS_Architecture_and_Build_Plan.md) and its PDF. Those documents remain historical references; they are not a claim that a runtime or ISO has already been built.

## Implementation evidence required

Validate private socket access, user service startup, model readiness, tool isolation, ISO live boot, clean installation, boot after media removal, persisted task history and the offline demo's declared local workflow. Record exact image, package, model and hypervisor versions with the test results.
