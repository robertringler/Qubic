"""Tests for report generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quasim.validation.mission_validator import ValidationResult
from quasim.validation.performance_comparison import (
    ComparisonMetrics,
    ComparisonReport,
)
from quasim.validation.report_generator import ReportGenerator


class TestReportGenerator:
    """Test ReportGenerator."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        return str(tmp_path / "reports")

    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create report generator."""
        return ReportGenerator(output_dir=temp_output_dir)

    @pytest.fixture
    def validation_result(self):
        """Create sample validation result."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        result.metadata["mission_type"] = "falcon9"
        return result

    @pytest.fixture
    def comparison_report(self):
        """Create sample comparison report."""
        report = ComparisonReport(
            mission_id="test_mission",
            simulation_id="test_sim",
        )
        report.metrics["altitude"] = ComparisonMetrics(
            rmse=50.0,
            mae=40.0,
            max_error=100.0,
            correlation=0.98,
            bias=10.0,
        )
        report.summary = {
            "total_variables": 1,
            "data_points": 10,
            "passed_checks": 1,
            "failed_checks": 0,
            "failure_details": [],
            "average_rmse": 50.0,
            "average_correlation": 0.98,
        }
        report.passed = True
        return report

    def test_init(self, generator, temp_output_dir):
        """Test initialization."""
        assert generator.output_dir == Path(temp_output_dir)
        assert generator.output_dir.exists()

    def test_generate_validation_report_json(
        self, generator, validation_result
    ):
        """Test JSON validation report generation."""
        report_path = generator.generate_validation_report(
            validation_result,
            output_format="json",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".json")

        # Verify content
        with open(report_path) as f:
            data = json.load(f)

        assert data["is_valid"] is True
        assert data["warning_count"] == 1
        assert "mission_type" in data["metadata"]

    def test_generate_validation_report_markdown(
        self, generator, validation_result
    ):
        """Test Markdown validation report generation."""
        report_path = generator.generate_validation_report(
            validation_result,
            output_format="markdown",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".md")

        # Verify content
        with open(report_path) as f:
            content = f.read()

        assert "Mission Data Validation Report" in content
        assert "PASSED" in content
        assert "Test warning" in content

    def test_generate_validation_report_invalid_format(
        self, generator, validation_result
    ):
        """Test report generation with invalid format."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            generator.generate_validation_report(
                validation_result,
                output_format="invalid",
            )

    def test_generate_comparison_report_json(
        self, generator, comparison_report
    ):
        """Test JSON comparison report generation."""
        report_path = generator.generate_comparison_report(
            comparison_report,
            output_format="json",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".json")

        # Verify content
        with open(report_path) as f:
            data = json.load(f)

        assert data["mission_id"] == "test_mission"
        assert data["passed"] is True
        assert "altitude" in data["metrics"]

    def test_generate_comparison_report_markdown(
        self, generator, comparison_report
    ):
        """Test Markdown comparison report generation."""
        report_path = generator.generate_comparison_report(
            comparison_report,
            output_format="markdown",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".md")

        # Verify content
        with open(report_path) as f:
            content = f.read()

        assert "QuASIM Performance Comparison Report" in content
        assert "test_mission" in content
        assert "PASSED" in content
        assert "altitude" in content

    def test_generate_combined_report_json(
        self, generator, validation_result, comparison_report
    ):
        """Test combined JSON report generation."""
        report_path = generator.generate_combined_report(
            validation_result,
            comparison_report,
            output_format="json",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".json")

        # Verify content
        with open(report_path) as f:
            data = json.load(f)

        assert "validation" in data
        assert "comparison" in data
        assert "overall_status" in data
        assert data["overall_status"] is True

    def test_generate_combined_report_markdown(
        self, generator, validation_result, comparison_report
    ):
        """Test combined Markdown report generation."""
        report_path = generator.generate_combined_report(
            validation_result,
            comparison_report,
            output_format="markdown",
        )

        assert Path(report_path).exists()
        assert report_path.endswith(".md")

        # Verify content
        with open(report_path) as f:
            content = f.read()

        assert "QuASIM Mission Data Integration Report" in content
        assert "Mission Data Validation Report" in content
        assert "QuASIM Performance Comparison Report" in content

    def test_generate_combined_report_failed(
        self, generator, comparison_report
    ):
        """Test combined report with validation failure."""
        validation_result = ValidationResult(is_valid=False)
        validation_result.add_error("Critical error")

        report_path = generator.generate_combined_report(
            validation_result,
            comparison_report,
            output_format="json",
        )

        with open(report_path) as f:
            data = json.load(f)

        assert data["overall_status"] is False

    def test_list_reports(self, generator, validation_result):
        """Test listing generated reports."""
        # Generate some reports
        generator.generate_validation_report(validation_result, "json")
        generator.generate_validation_report(validation_result, "markdown")

        reports = generator.list_reports()

        assert len(reports) >= 2
        assert any(r.endswith(".json") for r in reports)
        assert any(r.endswith(".md") for r in reports)
