#!/usr/bin/env python3
"""Check Lambda ZIP contents and verify handler imports from each archive."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
ARTIFACTS = {
    "orders-producer.zip": ("producer", "orders.producer.handler"),
    "orders-consumer.zip": ("consumer", "orders.consumer.handler"),
}
FORBIDDEN_PARTS = {"tests", "pytest", "moto", "botocore", "boto3"}


def expected_names(function: str) -> set[str]:
    package = SOURCE / "orders"
    roots = (package / "shared", package / function)
    paths = {package / "__init__.py"}
    for root in roots:
        paths.update(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return {path.relative_to(SOURCE).as_posix() for path in paths}


def validate(path: Path, module_name: str, expected: set[str]) -> None:
    if not path.is_file():
        raise ValueError(f"Missing artifact: {path}")

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if names != expected:
            missing = sorted(expected - names)
            extra = sorted(names - expected)
            raise ValueError(f"{path.name}: missing={missing}, unexpected={extra}")
        if any(part.lower() in FORBIDDEN_PARTS for name in names for part in name.split("/")):
            raise ValueError(f"{path.name}: contains a test or SDK dependency")
        if not zipfile.is_zipfile(path):
            raise ValueError(f"{path.name}: invalid ZIP")

    sys.path.insert(0, str(path))
    try:
        from importlib import import_module

        module = import_module(module_name)
    finally:
        sys.path.remove(str(path))
    if not callable(getattr(module, "handler", None)):
        raise ValueError(f"{path.name}: {module_name}.handler is not callable")
    for name in tuple(sys.modules):
        if name == "orders" or name.startswith("orders."):
            del sys.modules[name]
    from importlib import invalidate_caches

    invalidate_caches()
    print(f"Valid: {path.relative_to(ROOT)} ({path.stat().st_size} bytes), {module_name}.handler imports")


def main() -> int:
    try:
        for filename, (function, module_name) in ARTIFACTS.items():
            validate(ROOT / "dist" / filename, module_name, expected_names(function))
    except (OSError, ValueError, zipfile.BadZipFile, ImportError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
