"""Performance comparison between QuASIM simulations and real mission data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class ComparisonMetrics:
    """Metrics for comparing simulation vs real data.

    Attributes:
        rmse: Root Mean Square Error
        mae: Mean Absolute Error
        max_error: Maximum absolute error
        correlation: Correlation coefficient
        bias: Mean bias (simulation - real)
    """

    rmse: float = 0.0
    mae: float = 0.0
    max_error: float = 0.0
    correlation: float = 0.0
    bias: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "rmse": self.rmse,
            "mae": self.mae,
            "max_error": self.max_error,
            "correlation": self.correlation,
            "bias": self.bias,
        }


@dataclass
class ComparisonReport:
    """Report comparing QuASIM simulation to real mission data.

    Attributes:
        mission_id: Mission identifier
        simulation_id: Simulation run identifier
        metrics: Comparison metrics for each variable
        summary: Overall summary statistics
        passed: Whether comparison passed acceptance criteria
    """

    mission_id: str
    simulation_id: str
    metrics: dict[str, ComparisonMetrics] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    passed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mission_id": self.mission_id,
            "simulation_id": self.simulation_id,
            "metrics": {
                key: metric.to_dict() for key, metric in self.metrics.items()
            },
            "summary": self.summary,
            "passed": self.passed,
        }


class PerformanceComparator:
    """Compares QuASIM simulation results with real mission data.

    Performs statistical analysis and generates comparison metrics to evaluate
    QuASIM's predictive accuracy against actual flight telemetry.
    """

    def __init__(
        self,
        acceptance_thresholds: dict[str, float] | None = None,
    ):
        """Initialize performance comparator.

        Args:
            acceptance_thresholds: Dictionary of variable names to RMSE thresholds
        """
        self.acceptance_thresholds = acceptance_thresholds or {
            "altitude": 1000.0,  # meters
            "velocity": 50.0,  # m/s
            "position": 5000.0,  # meters
        }

    def compute_metrics(
        self,
        simulation_data: np.ndarray,
        real_data: np.ndarray,
    ) -> ComparisonMetrics:
        """Compute comparison metrics between simulation and real data.

        Args:
            simulation_data: Array of simulated values
            real_data: Array of real measured values

        Returns:
            ComparisonMetrics with computed statistics
        """
        if len(simulation_data) != len(real_data):
            raise ValueError(
                f"Data length mismatch: simulation={len(simulation_data)}, "
                f"real={len(real_data)}"
            )

        if len(simulation_data) == 0:
            return ComparisonMetrics()

        # Calculate errors
        errors = simulation_data - real_data
        abs_errors = np.abs(errors)

        metrics = ComparisonMetrics(
            rmse=float(np.sqrt(np.mean(errors**2))),
            mae=float(np.mean(abs_errors)),
            max_error=float(np.max(abs_errors)),
            bias=float(np.mean(errors)),
        )

        # Calculate correlation if data has variance
        if np.std(simulation_data) > 0 and np.std(real_data) > 0:
            metrics.correlation = float(
                np.corrcoef(simulation_data, real_data)[0, 1]
            )

        return metrics

    def compare_trajectories(
        self,
        simulation_trajectory: list[dict[str, Any]],
        real_trajectory: list[dict[str, Any]],
        variables: list[str] | None = None,
    ) -> dict[str, ComparisonMetrics]:
        """Compare simulation and real trajectories.

        Args:
            simulation_trajectory: List of simulation state dictionaries
            real_trajectory: List of real mission state dictionaries
            variables: List of variable names to compare (None for all common)

        Returns:
            Dictionary mapping variable names to ComparisonMetrics
        """
        if len(simulation_trajectory) != len(real_trajectory):
            # Interpolate or resample if lengths differ
            min_len = min(len(simulation_trajectory), len(real_trajectory))
            simulation_trajectory = simulation_trajectory[:min_len]
            real_trajectory = real_trajectory[:min_len]

        # Determine variables to compare
        if variables is None:
            # Find common variables
            sim_vars = set(simulation_trajectory[0].keys())
            real_vars = set(real_trajectory[0].keys())
            variables = list(sim_vars & real_vars)

        results = {}

        for var in variables:
            # Skip non-numeric variables
            if var in ["timestamp", "met", "vehicle_id", "vehicle_system"]:
                continue

            try:
                # Extract variable from trajectories
                sim_values = np.array([point.get(var, 0.0) for point in simulation_trajectory])
                real_values = np.array([point.get(var, 0.0) for point in real_trajectory])

                # Handle multidimensional variables (e.g., state_vector)
                if sim_values.ndim > 1 or isinstance(sim_values[0], (list, tuple)):
                    # Compute metrics for magnitude
                    sim_values = np.array([np.linalg.norm(v) for v in sim_values])
                    real_values = np.array([np.linalg.norm(v) for v in real_values])

                metrics = self.compute_metrics(sim_values, real_values)
                results[var] = metrics

            except (TypeError, ValueError, KeyError):
                # Skip variables that can't be compared
                continue

        return results

    def generate_report(
        self,
        mission_id: str,
        simulation_id: str,
        simulation_trajectory: list[dict[str, Any]],
        real_trajectory: list[dict[str, Any]],
    ) -> ComparisonReport:
        """Generate comprehensive comparison report.

        Args:
            mission_id: Mission identifier
            simulation_id: Simulation run identifier
            simulation_trajectory: Simulated trajectory data
            real_trajectory: Real mission trajectory data

        Returns:
            ComparisonReport with detailed analysis
        """
        report = ComparisonReport(
            mission_id=mission_id,
            simulation_id=simulation_id,
        )

        # Compare trajectories
        report.metrics = self.compare_trajectories(
            simulation_trajectory,
            real_trajectory,
        )

        # Check against acceptance thresholds
        passed_checks = []
        failed_checks = []

        for var, metrics in report.metrics.items():
            threshold = self.acceptance_thresholds.get(var)
            if threshold is not None:
                if metrics.rmse <= threshold:
                    passed_checks.append(var)
                else:
                    failed_checks.append(
                        f"{var}: RMSE={metrics.rmse:.2f} > {threshold:.2f}"
                    )

        report.passed = len(failed_checks) == 0

        # Generate summary
        report.summary = {
            "total_variables": len(report.metrics),
            "data_points": len(simulation_trajectory),
            "passed_checks": len(passed_checks),
            "failed_checks": len(failed_checks),
            "failure_details": failed_checks,
            "average_rmse": float(
                np.mean([m.rmse for m in report.metrics.values()])
            ) if report.metrics else 0.0,
            "average_correlation": float(
                np.mean([m.correlation for m in report.metrics.values()])
            ) if report.metrics else 0.0,
        }

        return report

    def compare_single_point(
        self,
        simulation_state: dict[str, Any],
        real_state: dict[str, Any],
    ) -> dict[str, float]:
        """Compare single state points.

        Args:
            simulation_state: Simulated state dictionary
            real_state: Real measured state dictionary

        Returns:
            Dictionary mapping variable names to absolute errors
        """
        errors = {}

        common_vars = set(simulation_state.keys()) & set(real_state.keys())

        for var in common_vars:
            if var in ["timestamp", "met", "vehicle_id", "vehicle_system"]:
                continue

            try:
                sim_val = simulation_state[var]
                real_val = real_state[var]

                # Handle scalar values
                if isinstance(sim_val, (int, float)) and isinstance(real_val, (int, float)):
                    errors[var] = abs(sim_val - real_val)

                # Handle vector values
                elif isinstance(sim_val, (list, tuple)) and isinstance(real_val, (list, tuple)) and len(sim_val) == len(real_val):
                    sim_arr = np.array(sim_val)
                    real_arr = np.array(real_val)
                    errors[var] = float(np.linalg.norm(sim_arr - real_arr))

            except (TypeError, ValueError):
                continue

        return errors
