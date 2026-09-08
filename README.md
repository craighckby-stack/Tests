# EMG Core — Test Suite & Bug-Fixing Harness

> **Engine Designation:** EMG Core v49 Neural Code and Documentation Optimizer  
> **Status:** Active / Production-Ready  

This directory contains specialized test modules populated with intentional bugs, regressions, and extreme edge cases. These artifacts serve as performance benchmarks and evaluation targets for the **EMG Core** neural code enhancer and automated remediation engine.

---

## Execution Environment

All test suites are executed and benchmarked on the **2.5 Flash Lite** model architecture.

### Quick Start

To execute the test suite against the target model, run the following command:

```bash
# Execute the comprehensive test harness on 2.5 Flash Lite
python -m emg_core.harness --model "2.5-flash-lite" --verbose
```