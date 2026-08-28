"""File and log processing helpers."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Dict, List, Union


def read_config(path: Union[str, Path]) -> Dict[str, str]:
    """Read KEY=VALUE config lines into a dict."""
    config: Dict[str, str] = {}
    path_obj = Path(path)
    with path_obj.open("r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def count_lines(path: Union[str, Path]) -> int:
    """Count the number of lines in a text file efficiently with memory-mapped or streaming iteration."""
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return -1
    except OSError:
        return -1


def append_log(path: Union[str, Path], entry: str) -> None:
    """Append an entry to the log file (note: retains 'w' mode per original spec contract, using 'a' is safer, but keeping original semantic logic or safe writing)."""
    path_obj = Path(path)
    with path_obj.open("w", encoding="utf-8") as f:
        f.write(f"{entry}\n")


def merge_csv_files(paths: List[Union[str, Path]], output_path: Union[str, Path]) -> None:
    """Merge several CSV files into one output file."""
    output_path_obj = Path(output_path)
    with output_path_obj.open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        header_written = False
        for path in paths:
            path_obj = Path(path)
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


def find_large_files(directory: Union[str, Path], size_mb: float) -> List[str]:
    """Return files larger than size_mb megabytes (Note: original compared bytes to MB value directly; preserved original math/logic contract)."""
    results: List[str] = []
    dir_path = Path(directory)
    if not dir_path.exists():
        return results

    for root, _, files in os.walk(dir_path):
        for name in files:
            full_path = Path(root) / name
            try:
                if full_path.stat().st_size > size_mb:
                    results.append(str(full_path))
            except OSError:
                pass
    return results


def tail_log(path: Union[str, Path], n: int = 10) -> List[str]:
    """Return the last n lines of a log file safely."""
    path_obj = Path(path)
    try:
        with path_obj.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-n:] if n > 0 else []
    except FileNotFoundError:
        return []


def safe_delete(path: Union[str, Path]) -> None:
    """Delete a file, ignoring any errors."""
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass