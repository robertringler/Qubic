# GitHub Copilot Tasks for QuASIM

This directory contains GitHub Copilot agent task definitions for automating complex, multi-step implementations in the QuASIM project.

## Overview

GitHub Copilot tasks are YAML-based specifications that instruct GitHub Copilot to perform comprehensive, end-to-end implementations. These tasks go beyond simple code generation to orchestrate entire subsystems with proper architecture, documentation, and testing.

## Available Tasks

### QuNimbus Cloud (`qunimbus_cloud.yaml`)

**Purpose**: Design and implement QuNimbus, a quantum-optimized cloud fabric purpose-built for QuASIM's quantum-classical workloads.

**Objectives**:
- Achieve ≥10× efficiency improvement vs AWS/GCP/Azure
- Implement quantum-aware scheduling and anti-holographic tensor compression
- Deliver compliance-first isolation domains (DO-178C L-A, CMMC 2.0 L2)
- Create RL-driven autoscaling and energy optimization
- Generate comprehensive SDK for quantum-classical orchestration

**Key Components**:
1. **Control Plane**: Quantum-aware Kubernetes scheduler with RL-based autoscaling
2. **Compute Fabric**: Multi-GPU quantum circuit simulation with cuQuantum/ROCm
3. **Storage System**: Anti-holographic compression and quantum elastic block store
4. **AI/RL Optimizer**: Reinforcement learning for scheduling and energy management
5. **Security Layer**: Fortinet integration, CAC authentication, CMMC 2.0 L2 compliance
6. **Networking**: Hybrid photonic-classical mesh with quantum key distribution
7. **CI/CD Pipeline**: Full observability stack (Prometheus, Grafana, Loki, Tempo)
8. **SDK**: Multi-language (Python, C++, Rust) for seamless integration
9. **Benchmarking**: Comparative analysis vs AWS/GCP/Azure/Oracle

**Deliverables**:
- Complete infrastructure as code (Terraform + Helm)
- Production-ready Kubernetes manifests
- Security and compliance configurations
- Developer SDK with documentation
- Comprehensive benchmark report demonstrating ≥10× efficiency gains

**Compliance Standards**:
- DO-178C Level A (Aerospace certification)
- CMMC 2.0 Level 2 (Defense contractor cybersecurity)
- NIST 800-53 Rev 5 HIGH baseline
- DFARS and DO-326A

## Usage

### Prerequisites

- GitHub Copilot access with agent capabilities
- Repository write access
- Kubernetes cluster (1.28+) for deployment testing
- Terraform 1.5+
- Python 3.10+
- Docker/containerd

### Executing a Task

To execute the QuNimbus Cloud task:

```bash
gh copilot-agent run .github/copilot-tasks/qunimbus_cloud.yaml
```

Or use GitHub Copilot CLI:

```bash
copilot task run qunimbus_cloud
```

### Task Structure

Each task YAML contains:

- **name**: Human-readable task name
- **description**: Detailed objective and scope
- **objectives**: Specific goals and targets
- **steps**: Ordered sequence of implementation steps
- **deliverables**: Expected outputs and artifacts
- **optional_enhancements**: Future improvements
- **success_metrics**: Quantitative performance targets
- **validation**: Testing and acceptance criteria

## Development Workflow

1. **Review Task Specification**: Understand objectives and deliverables
2. **Execute Task**: Run using GitHub Copilot agent
3. **Monitor Progress**: Check logs and intermediate outputs
4. **Validate Results**: Run automated tests and manual reviews
5. **Iterate**: Refine implementation based on validation results

## Best Practices

### Task Design

- **Specificity**: Define clear, measurable objectives
- **Modularity**: Break complex tasks into logical steps
- **Documentation**: Include comprehensive context and requirements
- **Validation**: Specify acceptance criteria and test strategies

### Execution

- **Incremental**: Execute steps incrementally, validating each
- **Version Control**: Commit task outputs regularly
- **Review**: Conduct thorough code and architecture reviews
- **Testing**: Run automated tests after each major component

## Task Validation

All tasks should be validated before execution:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/copilot-tasks/qunimbus_cloud.yaml'))"

# Check task structure
python3 scripts/validate_copilot_tasks.py
```

## Contributing New Tasks

To add a new Copilot task:

1. Create a new YAML file in this directory
2. Follow the structure of existing tasks (e.g., `qunimbus_cloud.yaml`)
3. Include all required sections: name, description, objectives, steps, deliverables
4. Add documentation to this README
5. Validate YAML syntax and structure
6. Submit for review with example execution results

### Task Template

```yaml
name: "Task Name"
description: |
  Detailed description of what this task accomplishes.

objectives:
  - Objective 1
  - Objective 2

steps:
  - name: "Step 1"
    id: "step-1"
    description: "What this step does"
    commands:
      - command: "bash command"
        description: "What this command does"
    outputs:
      - "Expected output files"

deliverables:
  category:
    - name: "Deliverable name"
      description: "What is delivered"

success_metrics:
  - metric: "Metric name"
    target: "Target value"

validation:
  automated_tests:
    - "Test description"
  acceptance_criteria:
    - "Criterion description"
```

## Support

For questions or issues with Copilot tasks:

1. Check task YAML syntax and structure
2. Review GitHub Copilot agent documentation
3. Consult QuASIM architecture documentation in `/docs`
4. Open an issue with `copilot-task` label

## Related Documentation

- [QuASIM README](../../README.md)
- [Architecture Documentation](../../docs/architecture/)
- [Compliance Documentation](../../COMPLIANCE_ASSESSMENT_INDEX.md)
- [Contributing Guide](../../CONTRIBUTING.md)

## License

All Copilot tasks are part of the QuASIM project and licensed under Apache 2.0.

See [LICENSE](../../LICENSE) for details.
