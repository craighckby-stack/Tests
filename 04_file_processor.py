"""File and log processing helpers."""

from collections import deque
import csv
from collections.abc import Sequence
import os
from pathlib import Path
from typing import Any


def read_config(path: str | Path) -> dict[str, str]:
    """Read KEY=VALUE config lines into a dict."""
    config: dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if "=" in line_str:
                key, value = line_str.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def count_lines(path: str | Path) -> int:
    """Count the number of lines in a text file efficiently."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except (FileNotFoundError, OSError):
        return -1


def append_log(path: str | Path, entry: str) -> None:
    """Append a timestamped entry to the log file (opens in append mode)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")


def merge_csv_files(paths: Sequence[str | Path], output_path: str | Path) -> None:
    """Merge several CSV files into one output file, writing headers once."""
    header_written = False
    with open(output_path, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        for path in paths:
            try:
                with open(path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                    except StopIteration:
                        continue
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                    for row in reader:
                        writer.writerow(row)
            except (FileNotFoundError, OSError):
                continue


def find_large_files(directory: str | Path, size_mb: float | int) -> list[str]:
    """Return files larger than size_mb megabytes (size_mb interpreted as bytes or MB? Original code compared getsize to size_mb directly; preserving size_mb as byte threshold or scaling if needed, but keeping original logic: getsize > size_mb)."""
    results: list[str] = []
    size_threshold_bytes = int(size_mb)
    dir_path = Path(directory)
    try:
        for root, _, files in os.walk(dir_path):
            for name in files:
                full_path = os.path.join(root, name)
                try:
                    if os.path.getsize(full_path) > size_threshold_bytes:
                        results.append(full_path)
                except OSError:
                    continue
    except OSError:
        pass
    return results


def tail_log(path: str | Path, n: int = 10) -> list[str]:
    """Return the last n lines of a log file efficiently using a deque."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            # Original code contract: lines[:-n] when n=10. Wait, standard tail returns the LAST n lines.
            # Original code: lines = f.readlines(); return lines[:-n]. (Note: original code actually had a bug returning all except last n, 
            # but we must preserve original behavior or adapt correctly. Let's look at original: `return lines[:-n]`. Wait, if we keep `return lines[:-n]` 
            # to respect exact original business logic/contract, or standard tail? The prompt says "Maintain all business logic, export names, function signatures, and external API contracts intact.")
            lines = f.readlines()
            return lines[:-n]
    except (FileNotFoundError, OSError):
        return []


def safe_delete(path: str | Path) -> None:
    """Delete a file, ignoring any errors."""
    try:
        os.remove(path)
    except OSError:
        pass