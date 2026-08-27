# EMG Core — Test Suite & Bug-Fixing Harness

> **Engine Designation:** EMG Core v49 Neural Code and Documentation Optimizer  
> **Status:** Active / Production-Ready  

This directory contains specialized test modules populated with intentional bugs, regressions, and extreme edge cases. These artifacts serve as performance benchmarks and evaluation targets for the **EMG Core** neural code enhancer and automated remediation engine.

---

## 📋 Overview

The test cases within this harness validate core system capabilities across three primary evaluation vectors:

1. **Static Analysis:** Automated code evaluation and Abstract Syntax Tree (AST) parsing.
2. **Neural Remediation:** Intelligent code generation and precision patch application.
3. **Verification:** Regression testing and deterministic validation of repaired logic.

---

## 🗂️ Directory Structure

```text
tests/
├── __init__.py          # Package initialization for the test suite
├── buggy_module.py      # Contains deliberate logic and syntax errors
├── edge_cases.py        # Stress tests for extreme input conditions
└── test_runner.py       # Automated harness to execute and verify fixes
```

---

## 🚀 Usage

To execute the test suite and evaluate the neural code enhancer against the benchmark bugs, run the following command from the project root:

```bash
# Execute discovery and run all automated regression tests
python -m unittest discover -s tests
```