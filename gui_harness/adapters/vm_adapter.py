"""
gui_harness.adapters.vm_adapter — VM-based backend configuration.

Configures the unified input system to route actions to a remote VM.
Also patches screenshot to download from VM.

Usage:
    from gui_harness.adapters.vm_adapter import patch_for_vm
    patch_for_vm("http://172.16.105.128:5000")
"""

from __future__ import annotations

import os
import json
import subprocess
import tempfile
import time


def patch_for_vm(vm_url: str):
    """Configure all subsystems to use the VM backend."""
    url = vm_url.rstrip("/")

    # 1. Configure input backend
    from gui_harness.action import input as _input
    _input.configure(vm_url=url)

    # 2. Patch screenshot to download from VM
    import gui_harness.perception.screenshot as _ss
    _ss.take = lambda path="/tmp/gui_agent_screen.png": _vm_screenshot(url, path)
    _ss.take_window = lambda app, out=None: _vm_screenshot(url, out or "/tmp/gui_agent_screen.png")


def _valid_image(path: str) -> bool:
    if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    try:
        from PIL import Image
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def _vm_screenshot(vm_url: str, path: str = "/tmp/gui_agent_screen.png") -> str:
    """Download a VM screenshot without ever replacing the target with bad bytes."""
    target_dir = os.path.dirname(path) or "."
    os.makedirs(target_dir, exist_ok=True)

    last_error = ""
    for attempt in range(3):
        fd, tmp_path = tempfile.mkstemp(prefix=".gui_agent_screen_", suffix=".png", dir=target_dir)
        os.close(fd)
        try:
            result = subprocess.run(
                [
                    "/usr/bin/curl",
                    "-fsS",
                    "--connect-timeout",
                    "10",
                    "-m",
                    "15",
                    "-o",
                    tmp_path,
                    f"{vm_url}/screenshot",
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0 and _valid_image(tmp_path):
                os.replace(tmp_path, path)
                return path
            last_error = (result.stderr or result.stdout or f"curl exit {result.returncode}").strip()
            response_body = _fetch_screenshot_error_body(vm_url) if result.returncode == 22 else ""
            if "Read-only file system" in response_body:
                last_error = f"{last_error}; VM screenshot service hit read-only filesystem"
            _save_failed_screenshot_attempt(
                tmp_path=tmp_path,
                vm_url=vm_url,
                target_path=path,
                attempt=attempt + 1,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                response_body=response_body,
            )
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        time.sleep(0.5 * (attempt + 1))

    raise RuntimeError(f"VM screenshot download failed or returned invalid image: {last_error}")


def _fetch_screenshot_error_body(vm_url: str) -> str:
    try:
        result = subprocess.run(
            [
                "/usr/bin/curl",
                "-sS",
                "--connect-timeout",
                "5",
                "-m",
                "10",
                f"{vm_url}/screenshot",
            ],
            capture_output=True,
            text=True,
            timeout=12,
        )
        body = result.stdout or result.stderr or ""
        return body[-4000:]
    except Exception as e:
        return f"failed to fetch error body: {e}"


def _save_failed_screenshot_attempt(
    *,
    tmp_path: str,
    vm_url: str,
    target_path: str,
    attempt: int,
    returncode: int,
    stdout: str,
    stderr: str,
    response_body: str = "",
) -> None:
    artifact_dir = os.environ.get("GUI_HARNESS_ARTIFACT_DIR")
    if not artifact_dir:
        return
    try:
        os.makedirs(artifact_dir, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        base = f"bad_screenshot_{stamp}_attempt{attempt}"
        bad_path = os.path.join(artifact_dir, f"{base}.bin")
        meta_path = os.path.join(artifact_dir, f"{base}.json")

        if os.path.exists(tmp_path):
            with open(tmp_path, "rb") as src, open(bad_path, "wb") as dst:
                dst.write(src.read())
        metadata = {
            "vm_url": vm_url,
            "target_path": target_path,
            "attempt": attempt,
            "returncode": returncode,
            "stdout": (stdout or "")[-2000:],
            "stderr": (stderr or "")[-2000:],
            "response_body": (response_body or "")[-4000:],
            "bytes": os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0,
            "valid_image": _valid_image(tmp_path),
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
    except Exception:
        pass
