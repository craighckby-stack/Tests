9/10

stupid bug @@@ still there 🤷

# EMG Core — Test Suite & Bug-Fixing Harness

> **Engine Designation:** EMG Core v49 Neural Code and Documentation Optimizer  
> **Status:** Active / Production-Ready  

---

## Overview

This directory houses specialized test modules pre-populated with intentional bugs, regressions, and extreme edge cases. These artifacts serve as standardized performance benchmarks and evaluation targets for the **EMG Core** neural code enhancer and automated remediation engine.

## Directory Structure & Modules

```text
emg-core-harness/
├── benchmarks/         # Performance and execution time benchmarks
├── edge-cases/         # Extreme boundary-condition test cases
├── regressions/        # Historical bug reproductions and regression suites
└── intentional-bugs/   # Seeded anomalies for neural remediation targets
```

## Usage Guidelines

To execute the test suite against the EMG Core remediation engine, run the following command:

```bash
# Execute the comprehensive test harness with default neural weights
emg-core test --mode=remediation --target=./benchmarks
```

## Contributing

When adding new test modules or intentional bugs to this harness, ensure they include proper documentation, clear expected outcomes, and adhere to the established EMG Core v49 schema.
