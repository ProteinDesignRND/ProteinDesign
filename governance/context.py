"""
Lightweight context derivation.

Derives environment and repository context safely without expensive operations
or speculative scientific inference.

Distinguishes DERIVED context from DECLARED context.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any


def derive_context(
    declared_context: Optional[Dict[str, Any]] = None,
    project_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Safely derive repository, environment, and runtime context.
    
    Returns a dictionary with:
      - 'declared': explicit values provided by the caller
      - 'derived': values safely discovered from git, environment, and runtime
      - 'effective': merged view where declared overrides derived for matching keys
      - 'provenance': tracking of which fields are DECLARED vs DERIVED
    """
    declared = dict(declared_context or {})
    derived: Dict[str, Any] = {}
    provenance: Dict[str, str] = {}

    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent
    else:
        project_root = Path(project_root)

    # 1. Python runtime
    derived["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    derived["platform"] = sys.platform
    derived["os_name"] = platform.system()

    # 2. Git context (safe execution)
    try:
        sha_res = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        if sha_res.returncode == 0:
            derived["git_sha"] = sha_res.stdout.strip()
        else:
            derived["git_sha"] = None
    except Exception:
        derived["git_sha"] = None

    try:
        branch_res = subprocess.run(
            ["git", "-C", str(project_root), "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        if branch_res.returncode == 0 and branch_res.stdout.strip():
            derived["git_branch"] = branch_res.stdout.strip()
        else:
            derived["git_branch"] = None
    except Exception:
        derived["git_branch"] = None

    # 3. Key dependency versions (using metadata to avoid heavy CUDA/DLL initialization)
    try:
        from importlib.metadata import version as get_version
    except ImportError:
        get_version = None

    for pkg in ("torch", "torch_geometric"):
        if pkg in sys.modules:
            mod = sys.modules[pkg]
            derived[f"{pkg}_version"] = getattr(mod, "__version__", "unknown")
        elif get_version:
            try:
                derived[f"{pkg}_version"] = get_version(pkg)
            except Exception:
                derived[f"{pkg}_version"] = None
        else:
            derived[f"{pkg}_version"] = None

    # 4. Working directory & experiment ID detection
    cwd = Path.cwd()
    derived["cwd"] = str(cwd)
    if "experiments" in cwd.parts:
        try:
            exp_idx = cwd.parts.index("experiments")
            if len(cwd.parts) > exp_idx + 1:
                derived["detected_experiment_dir"] = cwd.parts[exp_idx + 1]
        except Exception:
            pass

    # 5. Merge into effective context with provenance tracking
    effective = dict(derived)
    for k in derived:
        provenance[k] = "DERIVED"

    for k, v in declared.items():
        effective[k] = v
        provenance[k] = "DECLARED"

    return {
        "declared": declared,
        "derived": derived,
        "effective": effective,
        "provenance": provenance,
    }
