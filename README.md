# Test Suite & Bug-Fixing Harness

This directory contains test files (e.g., Python scripts and other modules) populated with intentional bugs, regressions, and edge cases. These files serve as benchmarks and targets for the **EMG Core** neural code enhancer and automated remediation engine.

## Overview

The test cases herein are designed to validate the system's capabilities in:
- Automated code analysis and abstract syntax tree (AST) parsing.
- Neural code generation and patch application.
- Regression testing and verification of fixed logic.

## Directory Structure

```text
tests/
├── __init__.py
├── buggy_module.py      # Contains intentional logic and syntax errors
├── edge_cases.py        # Stress tests for extreme input conditions
└── test_runner.py       # Automated harness to execute and verify fixes
```

## Usage

To run the test suite and evaluate the enhancer against these bugs, execute the following command:

```bash
python -m unittest discover -s tests
```