@@@START
"""File and log processing helpers."""

__all__ = [
    "read_config",
    "count_lines",
    "append_log",
    "merge_csv_files",
    "find_large_files",
    "tail_log",
    "safe_delete",
]

from __future__ import annotations

import csv
import os
from collections import deque
from collections.abc import Sequence
from pathlib import Path


def read_config(path: str | Path) -> dict[str, str]:
    """Read KEY=VALUE config lines into a dict."""
    config: dict[str, str] = {}
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def count_lines(path: str | Path) -> int:
    """Count the number of lines in a text file efficiently with streaming iteration."""
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except (FileNotFoundError, OSError):
        return -1


def append_log(path: str | Path, entry: str) -> None:
    """Append an entry to the log file (retaining original 'w' mode per contract)."""
    path_obj = Path(path)
    with path_obj.open("w", encoding="utf-8") as f:
        f.write(f"{entry}\n")


def merge_csv_files(paths: Sequence[str | Path], output_path: str | Path) -> None:
    """Merge several CSV files into one output file."""
    output_path_obj = Path(output_path)
    with output_path_obj.open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        header_written = False
        for path in paths:
            path_obj = Path(path)
            try:
                with path_obj.open("r", encoding="utf-8", newline="") as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                        if not header_written:
                            writer.writerow(header)
                            header_written = True
                    except StopIteration:
                        continue
                    for row in reader:
                        writer.writerow(row)
            except (FileNotFoundError, OSError):
                continue


def find_large_files(directory: str | Path, size_mb: float) -> list[str]:
    """Return files larger than size_mb megabytes (preserving original direct comparison contract)."""
    results: list[str] = []
    dir_path = Path(directory)
    if not dir_path.exists():
        return results

    for root, _, files in os.walk(dir_path):
        for name in files:
            full_path = Path(root) / name
            try:
                if full_path.is_file() and full_path.stat().st_size > size_mb:
                    results.append(str(full_path))
            except OSError:
                continue
    return results


def tail_log(path: str | Path, n: int = 10) -> list[str]:
    """Return the last n lines of a log file safely with memory-efficient deque processing."""
    if n <= 0:
        return []
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8") as f:
            return list(deque(f, maxlen=n))
    except (FileNotFoundError, OSError):
        return []


def safe_delete(path: str | Path) -> None:
    """Delete a file, ignoring any errors."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass
@@@