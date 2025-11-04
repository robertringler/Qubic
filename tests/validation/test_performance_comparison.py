"""Tests for performance comparison module."""

from __future__ import annotations

import numpy as np
import pytest

from quasim.validation.performance_comparison import (
    ComparisonMetrics,
    ComparisonReport,
    PerformanceComparator,
)


class TestComparisonMetrics:
    """Test ComparisonMetrics dataclass."""

    def test_init_default(self):
        """Test default initialization."""
        metrics = ComparisonMetrics()
        assert metrics.rmse == 0.0
        assert metrics.mae == 0.0
        assert metrics.max_error == 0.0
        assert metrics.correlation == 0.0
        assert metrics.bias == 0.0

    def test_to_dict(self):
        """Test dictionary conversion."""
        metrics = ComparisonMetrics(
            rmse=1.5,
            mae=1.0,
            max_error=3.0,
            correlation=0.95,
            bias=0.5,
        )

        data = metrics.to_dict()
        assert data["rmse"] == 1.5
        assert data["mae"] == 1.0
        assert data["max_error"] == 3.0
        assert data["correlation"] == 0.95
        assert data["bias"] == 0.5


class TestComparisonReport:
    """Test ComparisonReport dataclass."""

    def test_init(self):
        """Test initialization."""
        report = ComparisonReport(
            mission_id="test_mission",
            simulation_id="test_sim",
        )
        assert report.mission_id == "test_mission"
        assert report.simulation_id == "test_sim"
        assert not report.passed
        assert len(report.metrics) == 0

    def test_to_dict(self):
        """Test dictionary conversion."""
        report = ComparisonReport(
            mission_id="test_mission",
            simulation_id="test_sim",
        )
        report.metrics["altitude"] = ComparisonMetrics(rmse=100.0)
        report.summary["total_variables"] = 1
        report.passed = True

        data = report.to_dict()
        assert data["mission_id"] == "test_mission"
        assert data["passed"] is True
        assert "altitude" in data["metrics"]
        assert data["summary"]["total_variables"] == 1


class TestPerformanceComparator:
    """Test PerformanceComparator."""

    def test_init_default(self):
        """Test default initialization."""
        comparator = PerformanceComparator()
        assert "altitude" in comparator.acceptance_thresholds
        assert "velocity" in comparator.acceptance_thresholds

    def test_init_custom_thresholds(self):
        """Test initialization with custom thresholds."""
        thresholds = {"altitude": 500.0, "velocity": 25.0}
        comparator = PerformanceComparator(acceptance_thresholds=thresholds)
        assert comparator.acceptance_thresholds["altitude"] == 500.0
        assert comparator.acceptance_thresholds["velocity"] == 25.0

    def test_compute_metrics_identical(self):
        """Test metrics computation with identical data."""
        comparator = PerformanceComparator()

        sim_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        real_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        metrics = comparator.compute_metrics(sim_data, real_data)

        assert metrics.rmse == 0.0
        assert metrics.mae == 0.0
        assert metrics.max_error == 0.0
        assert metrics.bias == 0.0
        assert abs(metrics.correlation - 1.0) < 1e-10

    def test_compute_metrics_with_errors(self):
        """Test metrics computation with errors."""
        comparator = PerformanceComparator()

        sim_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        real_data = np.array([1.5, 2.5, 3.5, 4.5, 5.5])

        metrics = comparator.compute_metrics(sim_data, real_data)

        assert metrics.rmse > 0.0
        assert metrics.mae == 0.5  # Constant error of 0.5
        assert metrics.max_error == 0.5
        assert metrics.bias == -0.5
        assert metrics.correlation > 0.99  # Still highly correlated

    def test_compute_metrics_mismatched_length(self):
        """Test metrics computation with mismatched lengths."""
        comparator = PerformanceComparator()

        sim_data = np.array([1.0, 2.0, 3.0])
        real_data = np.array([1.0, 2.0])

        with pytest.raises(ValueError, match="Data length mismatch"):
            comparator.compute_metrics(sim_data, real_data)

    def test_compute_metrics_empty(self):
        """Test metrics computation with empty data."""
        comparator = PerformanceComparator()

        sim_data = np.array([])
        real_data = np.array([])

        metrics = comparator.compute_metrics(sim_data, real_data)
        assert metrics.rmse == 0.0

    def test_compare_trajectories_identical(self):
        """Test trajectory comparison with identical data."""
        comparator = PerformanceComparator()

        trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0, "velocity": 100.0},
            {"timestamp": 1.0, "altitude": 2000.0, "velocity": 200.0},
            {"timestamp": 2.0, "altitude": 3000.0, "velocity": 300.0},
        ]

        results = comparator.compare_trajectories(trajectory, trajectory)

        assert "altitude" in results
        assert "velocity" in results
        assert results["altitude"].rmse == 0.0
        assert results["velocity"].rmse == 0.0

    def test_compare_trajectories_with_differences(self):
        """Test trajectory comparison with differences."""
        comparator = PerformanceComparator()

        sim_trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0, "velocity": 100.0},
            {"timestamp": 1.0, "altitude": 2000.0, "velocity": 200.0},
        ]

        real_trajectory = [
            {"timestamp": 0.0, "altitude": 1100.0, "velocity": 105.0},
            {"timestamp": 1.0, "altitude": 2100.0, "velocity": 205.0},
        ]

        results = comparator.compare_trajectories(sim_trajectory, real_trajectory)

        assert results["altitude"].rmse > 0.0
        assert results["velocity"].rmse > 0.0

    def test_compare_trajectories_length_mismatch(self):
        """Test trajectory comparison with length mismatch."""
        comparator = PerformanceComparator()

        sim_trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0},
            {"timestamp": 1.0, "altitude": 2000.0},
            {"timestamp": 2.0, "altitude": 3000.0},
        ]

        real_trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0},
            {"timestamp": 1.0, "altitude": 2000.0},
        ]

        # Should truncate to shorter length
        results = comparator.compare_trajectories(sim_trajectory, real_trajectory)
        assert "altitude" in results

    def test_generate_report_passed(self):
        """Test report generation with passing criteria."""
        comparator = PerformanceComparator(
            acceptance_thresholds={"altitude": 200.0, "velocity": 20.0}
        )

        sim_trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0, "velocity": 100.0},
            {"timestamp": 1.0, "altitude": 2000.0, "velocity": 200.0},
        ]

        real_trajectory = [
            {"timestamp": 0.0, "altitude": 1050.0, "velocity": 105.0},
            {"timestamp": 1.0, "altitude": 2050.0, "velocity": 205.0},
        ]

        report = comparator.generate_report(
            mission_id="test_mission",
            simulation_id="test_sim",
            simulation_trajectory=sim_trajectory,
            real_trajectory=real_trajectory,
        )

        assert report.mission_id == "test_mission"
        assert report.passed
        assert len(report.metrics) > 0
        assert report.summary["data_points"] == 2

    def test_generate_report_failed(self):
        """Test report generation with failing criteria."""
        comparator = PerformanceComparator(
            acceptance_thresholds={"altitude": 10.0}  # Very tight threshold
        )

        sim_trajectory = [
            {"timestamp": 0.0, "altitude": 1000.0},
            {"timestamp": 1.0, "altitude": 2000.0},
        ]

        real_trajectory = [
            {"timestamp": 0.0, "altitude": 1100.0},
            {"timestamp": 1.0, "altitude": 2100.0},
        ]

        report = comparator.generate_report(
            mission_id="test_mission",
            simulation_id="test_sim",
            simulation_trajectory=sim_trajectory,
            real_trajectory=real_trajectory,
        )

        assert not report.passed
        assert len(report.summary["failure_details"]) > 0

    def test_compare_single_point_scalars(self):
        """Test single point comparison with scalar values."""
        comparator = PerformanceComparator()

        sim_state = {"altitude": 1000.0, "velocity": 100.0}
        real_state = {"altitude": 1050.0, "velocity": 105.0}

        errors = comparator.compare_single_point(sim_state, real_state)

        assert "altitude" in errors
        assert "velocity" in errors
        assert errors["altitude"] == 50.0
        assert errors["velocity"] == 5.0

    def test_compare_single_point_vectors(self):
        """Test single point comparison with vector values."""
        comparator = PerformanceComparator()

        sim_state = {"state_vector": [1.0, 2.0, 3.0]}
        real_state = {"state_vector": [1.1, 2.1, 3.1]}

        errors = comparator.compare_single_point(sim_state, real_state)

        assert "state_vector" in errors
        assert errors["state_vector"] > 0.0
