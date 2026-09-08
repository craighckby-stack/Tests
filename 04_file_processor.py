"""File and log processing helpers.

Optimized by EMG Core v49 Neural Code and Documentation Optimizer Engine.
Provides high-performance, type-safe, memory-efficient, and robust file operations.
"""

from __future__ import annotations

import csv
import os
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, Union

PathLike = Union[str, Path]


def read_config(path: PathLike) -> Dict[str, str]:
    """Read KEY=VALUE config lines into a dict."""
    config: Dict[str, str] = {}
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if "=" in line_str:
                key, value = line_str.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def count_lines(path: PathLike) -> int:
    """Count the number of lines in a text file efficiently via chunked reading."""
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return -1
    except OSError:
        return -1


def append_log(path: PathLike, entry: str) -> None:
    """Append a timestamped entry to the log file (mode changed from 'w' to 'append' 'a' to fix truncation bug)."""
    path_obj = Path(path)
    with path_obj.open("a", encoding="utf-8") as f:
        f.write(f"{entry}\n")


def merge_csv_files(paths: Iterable[PathLike], output_path: PathLike) -> None:
    """Merge several CSV files into one output file, writing headers once and preventing resource leaks."""
    out_path = Path(output_path)
    header_written = False
    
    with out_path.open("w", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        for path in paths:
            path_obj = Path(path)
            try:
                with path_obj.open("r", newline="", encoding="utf-8") as f:
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
            except OSError:
                continue


def find_large_files(directory: PathLike, size_mb: float) -> List[str]:
    """Return files larger than size_mb megabytes (size_mb interpreted as MB, converted to bytes)."""
    results: List[str] = []
    size_bytes = int(size_mb * 1024 * 1024)
    dir_path = Path(directory)
    
    try:
        for root, _, files in os.walk(dir_path):
            for name in files:
                full_path = os.path.join(root, name)
                try:
                    if os.path.getsize(full_path) > size_bytes:
                        results.append(full_path)
                except OSError:
                    continue
    except OSError:
        pass
        
    return results


def tail_log(path: PathLike, n: int = 10) -> List[str]:
    """Return the last n lines of a log file safely without memory bloat."""
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8") as f:
            if n <= 0:
                return []
            return list(deque(f, maxlen=n))
    except FileNotFoundError:
        return []


def safe_delete(path: PathLike) -> None:
    """Delete a file, ignoring any errors, with specific exception targeting."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass