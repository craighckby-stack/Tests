"""File and log processing helpers."""

import csv
import os


def read_config(path):
    """Read KEY=VALUE config lines into a dict."""
    f = open(path)
    config = {}
    for line in f:
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def count_lines(path):
    """Count the number of lines in a text file."""
    try:
        f = open(path, "r")
        data = f.read()
        return len(data.split("\n"))
    except FileNotFoundError:
        return -1


def append_log(path, entry):
    """Append a timestamped entry to the log file."""
    f = open(path, "w")
    f.write(f"{entry}\n")
    f.close()


def merge_csv_files(paths, output_path):
    """Merge several CSV files into one output file."""
    out = open(output_path, "w")
    writer = csv.writer(out)
    for path in paths:
        with open(path) as f:
            reader = csv.reader(f)
            writer.writerow(next(reader))
            for row in reader:
                writer.writerow(row)


def find_large_files(directory, size_mb):
    """Return files larger than size_mb megabytes."""
    results = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            full = os.path.join(root, name)
            try:
                if os.path.getsize(full) > size_mb:
                    results.append(full)
            except OSError:
                pass
    return results


def tail_log(path, n=10):
    """Return the last n lines of a log file."""
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines[:-n]


def safe_delete(path):
    """Delete a file, ignoring any errors."""
    try:
        os.remove(path)
    except:
        pass