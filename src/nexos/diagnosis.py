"""Static manifest inspection with a deterministic plan and verified report."""

from __future__ import annotations

import hashlib
import json
import tomllib
import uuid
from pathlib import Path

from .journal import Journal
from .plan import diagnosis_plan, validate_plan
from .policy import FileCapabilities


def inspect_manifests(capabilities: FileCapabilities) -> list[dict]:
    findings = []
    for filename in sorted(capabilities.MANIFESTS):
        if not capabilities.manifest_exists(filename):
            continue
        raw = capabilities.read_manifest(filename)
        decoded = raw.decode("utf-8")
        if filename == "package.json":
            data = json.loads(decoded)
            if not isinstance(data, dict):
                raise ValueError("package.json must contain an object")
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})
            if not isinstance(dependencies, dict) or not isinstance(dev_dependencies, dict):
                raise ValueError("Node dependency sections must be objects")
            count = len(set(dependencies) | set(dev_dependencies))
            kind = "Node declared package metadata"
        elif filename == "pyproject.toml":
            data = tomllib.loads(decoded)
            project = data.get("project", {})
            if not isinstance(project, dict):
                raise ValueError("Python project metadata must be a table")
            dependencies = project.get("dependencies", [])
            if not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies):
                raise ValueError("Python declared dependencies must be a list of strings")
            count = len(dependencies)
            kind = "Python declared project metadata"
        else:
            count = len([line for line in decoded.splitlines() if line.strip() and not line.lstrip().startswith("#")])
            kind = "Python requirements entries including directives"
        findings.append({"filename": filename, "kind": kind, "declared_entries": count,
                         "sha256": hashlib.sha256(raw).hexdigest()})
    if not findings:
        raise ValueError("No supported manifest was found in the granted project root")
    return findings


def render_report(task_id: str, findings: list[dict]) -> bytes:
    lines = ["# NEXOS Static Project Diagnosis", "", f"Task ID: {task_id}", "",
             "Scope: static inspection of supported manifests in the explicitly granted project root.",
             "Declared entries describe source metadata. Installed dependency and runtime compatibility need later Linux adapters.",
             "", "## Findings", ""]
    for finding in findings:
        # Only fixed adapter names, numeric counts and digests enter this report.
        lines += [f"### {finding['filename']}", f"Kind: {finding['kind']}",
                  f"Declared entries: {finding['declared_entries']}", f"Source SHA256: {finding['sha256']}", ""]
    lines += ["## Execution evidence", "", "Registered tools: manifest.inspect, report.create, report.verify.",
              "Project code execution: none. Network operations: none.",
              "Final verification is recorded in the separate task journal and CLI result.", ""]
    return "\n".join(lines).encode("utf-8")


def verify_report(capabilities: FileCapabilities, name: str, task_id: str,
                  findings: list[dict], expected_hash: str) -> dict:
    raw = capabilities.read_report(name)
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError("Report content changed before verification")
    text = raw.decode("utf-8")
    if f"Task ID: {task_id}\n" not in text or "## Findings\n" not in text:
        raise ValueError("Report identity or required section is missing")
    for finding in findings:
        if f"### {finding['filename']}\n" not in text or f"Source SHA256: {finding['sha256']}\n" not in text:
            raise ValueError("Report is missing manifest evidence")
        current = hashlib.sha256(capabilities.read_manifest(finding["filename"])).hexdigest()
        if current != finding["sha256"]:
            raise ValueError("Source manifest changed during diagnosis")
    return {"report_hash_matches": True, "task_identity_matches": True,
            "required_findings_present": True, "source_manifests_unchanged": True}


def diagnose(project: str | Path, output: str | Path, state: str | Path) -> dict:
    capabilities = FileCapabilities(project, output)
    task_id = uuid.uuid4().hex
    journal = Journal(state)
    try:
        journal.create(task_id, {"kind": "static_diagnosis", "project": str(capabilities.project),
                                 "output": str(capabilities.output)})
        plan = validate_plan(diagnosis_plan())
        journal.record(task_id, "PLANNED", {"steps": plan})
        journal.record(task_id, "RUNNING", {"tool": "manifest.inspect"})
        findings = inspect_manifests(capabilities)
        content = render_report(task_id, findings)
        filename = f"diagnosis-{task_id}.md"
        report = capabilities.write_report(filename, content)
        digest = hashlib.sha256(content).hexdigest()
        journal.record(task_id, "VERIFYING", {"report": str(report)})
        evidence = verify_report(capabilities, filename, task_id, findings, digest)
        result = {"task_id": task_id, "status": "SUCCEEDED", "scope": "static_manifest_inspection",
                  "report": str(report), "report_sha256": digest, "findings": findings,
                  "verification": evidence}
        journal.finish(task_id, result)
        return result
    except Exception as error:
        journal.record(task_id, "FAILED", {"error_type": type(error).__name__, "reason": str(error)})
        raise
    finally:
        journal.close()
