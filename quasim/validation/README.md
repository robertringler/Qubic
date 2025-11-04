# QuASIM Mission Data Validation Module

This module provides comprehensive mission data validation and performance comparison tools for QuASIM simulations against real flight telemetry data from SpaceX Falcon 9 and NASA Orion/SLS missions.

## Overview

The validation module enables:

1. **Data Ingestion**: Import real mission telemetry from SpaceX and NASA sources
2. **Data Validation**: Verify data completeness, physical plausibility, and temporal consistency
3. **Simulation Comparison**: Run QuASIM simulations and compare predictions to actual mission data
4. **Performance Reporting**: Generate detailed statistical analysis and comparison reports

## Components

### Mission Data Validator

Validates mission telemetry data for:
- Data completeness (required fields present)
- Physical range validation (altitude, velocity, etc.)
- Temporal consistency (monotonic timestamps)

```python
from quasim.validation import MissionDataValidator

validator = MissionDataValidator(mission_type="falcon9")
result = validator.validate_full(mission_data)

if result.is_valid:
    print("✅ Validation passed")
else:
    print(f"❌ {result.error_count} errors found")
```

### Performance Comparator

Compares simulation predictions to real mission data with metrics:
- Root Mean Square Error (RMSE)
- Mean Absolute Error (MAE)
- Maximum Error
- Correlation Coefficient
- Bias

```python
from quasim.validation import PerformanceComparator

comparator = PerformanceComparator(
    acceptance_thresholds={
        "altitude": 1000.0,  # meters
        "velocity": 50.0,    # m/s
    }
)

report = comparator.generate_report(
    mission_id="Falcon9_Mission",
    simulation_id="quasim_sim_001",
    simulation_trajectory=sim_data,
    real_trajectory=real_data,
)

print(f"Comparison {'✅ PASSED' if report.passed else '❌ FAILED'}")
```

### Report Generator

Generates comprehensive reports in JSON or Markdown format:

```python
from quasim.validation import ReportGenerator

generator = ReportGenerator(output_dir="reports")

# Generate combined validation and comparison report
report_path = generator.generate_combined_report(
    validation_result,
    comparison_report,
    output_format="markdown",
)

print(f"Report generated: {report_path}")
```

### Mission Data Integrator

Orchestrates the complete workflow:

```python
from quasim.validation.mission_integration import MissionDataIntegrator

# For SpaceX Falcon 9 missions
integrator = MissionDataIntegrator(
    mission_type="falcon9",
    output_dir="reports/falcon9",
)

results = integrator.process_spacex_mission(
    mission_id="Falcon9_Starlink_6-25",
    telemetry_batch=falcon9_telemetry_data,
    output_format="markdown",
)

# For NASA Orion/SLS missions
integrator = MissionDataIntegrator(
    mission_type="orion",
    output_dir="reports/orion",
)

results = integrator.process_nasa_mission(
    mission_id="Artemis_I",
    log_file_path="nasa_telemetry.csv",
    output_format="markdown",
)
```

## Supported Mission Types

### SpaceX Falcon 9
- **Data Format**: JSON telemetry batches
- **Required Fields**: timestamp, vehicle_id, altitude, velocity
- **Optional Fields**: thrust, throttle, attitude quaternion, angular rates
- **Validation Ranges**:
  - Altitude: 0 to 500,000 m
  - Velocity: 0 to 12,000 m/s
  - Throttle: 40 to 100%

### NASA Orion/SLS
- **Data Format**: CSV log files
- **Required Fields**: MET, vehicle_system, state_vector (6 elements)
- **Optional Fields**: GNC_mode, control_data, sensor_data
- **Validation Ranges**:
  - Position magnitude: 6,000 to 50,000 km
  - Velocity magnitude: 0 to 15,000 m/s

## Example Usage

See `examples/mission_data_integration_example.py` for complete examples:

```bash
cd /home/runner/work/QuASIM/QuASIM
python3 examples/mission_data_integration_example.py
```

## Report Format

### Markdown Report Structure

```markdown
# QuASIM Mission Data Integration Report

**Overall Status:** ✅ PASSED / ❌ FAILED

## Validation Results
- Status: ✅ PASSED
- Errors: 0
- Warnings: 2

## Performance Comparison
- Mission ID: Falcon9_Mission
- Total Variables: 5
- Data Points: 100
- Average RMSE: 45.23
- Average Correlation: 0.9876

## Detailed Metrics
| Variable | RMSE | MAE | Max Error | Correlation | Bias |
|----------|------|-----|-----------|-------------|------|
| altitude | 123.4 | 98.5 | 250.0 | 0.995 | -12.3 |
| velocity | 15.2 | 12.1 | 30.5 | 0.998 | 2.4 |
```

### JSON Report Structure

```json
{
  "validation": {
    "is_valid": true,
    "error_count": 0,
    "warning_count": 2,
    "errors": [],
    "warnings": ["Minor data gap detected"],
    "metadata": {
      "mission_type": "falcon9",
      "data_points_validated": 100
    }
  },
  "comparison": {
    "mission_id": "Falcon9_Mission",
    "simulation_id": "quasim_sim_001",
    "passed": true,
    "metrics": {
      "altitude": {
        "rmse": 123.4,
        "mae": 98.5,
        "max_error": 250.0,
        "correlation": 0.995,
        "bias": -12.3
      }
    },
    "summary": {
      "total_variables": 5,
      "data_points": 100,
      "average_rmse": 45.23,
      "average_correlation": 0.9876
    }
  }
}
```

## Acceptance Criteria

Default acceptance thresholds:
- Altitude RMSE: ≤ 1000 m
- Velocity RMSE: ≤ 50 m/s
- Position RMSE: ≤ 5000 m

Custom thresholds can be configured:

```python
comparator = PerformanceComparator(
    acceptance_thresholds={
        "altitude": 500.0,    # Tighter threshold
        "velocity": 25.0,
        "custom_var": 100.0,
    }
)
```

## Testing

Run the validation module tests:

```bash
# Run all validation tests
python3 -m pytest tests/validation/ -v

# Run specific test file
python3 -m pytest tests/validation/test_mission_validator.py -v

# Run integration tests
python3 -m pytest tests/validation/test_integration.py -v
```

## Architecture

```
quasim/validation/
├── __init__.py                    # Module exports
├── mission_validator.py           # Data validation logic
├── performance_comparison.py      # Comparison metrics and reporting
├── report_generator.py            # Report generation (JSON/MD)
├── mission_integration.py         # Main workflow orchestration
└── README.md                      # This file

tests/validation/
├── __init__.py
├── test_mission_validator.py      # Validator tests
├── test_performance_comparison.py # Comparison tests
├── test_report_generator.py       # Report generation tests
└── test_integration.py            # End-to-end workflow tests
```

## Dependencies

- **numpy**: Numerical computations and metrics
- **pandas**: Optional, for advanced data analysis
- Telemetry adapters from `telemetry_api` module
- Digital twin simulation from `quasim.dtwin` module

## Future Enhancements

Potential improvements:
1. Support for additional mission types (Crew Dragon, Starship)
2. Real-time telemetry streaming integration
3. Advanced statistical analysis (confidence intervals, hypothesis testing)
4. Interactive visualization dashboards (Plotly, Dash)
5. Machine learning-based anomaly detection
6. Multi-mission comparative analysis

## Contributing

When adding new mission types:

1. Update `MissionDataValidator._load_validation_rules()` with validation rules
2. Add telemetry adapter in `telemetry_api` module
3. Update `MissionDataIntegrator` to support new mission type
4. Add comprehensive tests in `tests/validation/`
5. Update this README with new mission type documentation

## License

See repository LICENSE file for details.
