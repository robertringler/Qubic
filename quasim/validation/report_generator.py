"""Report generation for mission data validation and comparison."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .mission_validator import ValidationResult
from .performance_comparison import ComparisonReport


class ReportGenerator:
    """Generates detailed performance comparison reports.

    Creates comprehensive reports comparing QuASIM simulations with real
    mission data, including statistical analysis, visualizations, and
    acceptance criteria evaluations.
    """

    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator.

        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_validation_report(
        self,
        validation_result: ValidationResult,
        output_format: str = "json",
    ) -> str:
        """Generate validation report.

        Args:
            validation_result: Validation result to report
            output_format: Output format ('json', 'markdown', 'html')

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format == "json":
            filename = f"validation_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w") as f:
                json.dump(validation_result.to_dict(), f, indent=2)

        elif output_format == "markdown":
            filename = f"validation_{timestamp}.md"
            filepath = self.output_dir / filename

            content = self._generate_validation_markdown(validation_result)
            with open(filepath, "w") as f:
                f.write(content)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return str(filepath)

    def _generate_validation_markdown(self, result: ValidationResult) -> str:
        """Generate markdown validation report."""
        lines = [
            "# Mission Data Validation Report",
            "",
            f"**Status:** {'✅ PASSED' if result.is_valid else '❌ FAILED'}",
            f"**Errors:** {result.error_count}",
            f"**Warnings:** {result.warning_count}",
            "",
        ]

        if result.errors:
            lines.extend([
                "## Errors",
                "",
            ])
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")

        if result.warnings:
            lines.extend([
                "## Warnings",
                "",
            ])
            for warning in result.warnings:
                lines.append(f"- {warning}")
            lines.append("")

        if result.metadata:
            lines.extend([
                "## Metadata",
                "",
            ])
            for key, value in result.metadata.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        return "\n".join(lines)

    def generate_comparison_report(
        self,
        comparison_report: ComparisonReport,
        output_format: str = "json",
    ) -> str:
        """Generate performance comparison report.

        Args:
            comparison_report: Comparison report to output
            output_format: Output format ('json', 'markdown', 'html')

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format == "json":
            filename = f"comparison_{comparison_report.mission_id}_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w") as f:
                json.dump(comparison_report.to_dict(), f, indent=2)

        elif output_format == "markdown":
            filename = f"comparison_{comparison_report.mission_id}_{timestamp}.md"
            filepath = self.output_dir / filename

            content = self._generate_comparison_markdown(comparison_report)
            with open(filepath, "w") as f:
                f.write(content)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return str(filepath)

    def _generate_comparison_markdown(self, report: ComparisonReport) -> str:
        """Generate markdown comparison report."""
        lines = [
            "# QuASIM Performance Comparison Report",
            "",
            f"**Mission ID:** {report.mission_id}",
            f"**Simulation ID:** {report.simulation_id}",
            f"**Status:** {'✅ PASSED' if report.passed else '❌ FAILED'}",
            "",
            "## Summary",
            "",
            f"- **Total Variables:** {report.summary.get('total_variables', 0)}",
            f"- **Data Points:** {report.summary.get('data_points', 0)}",
            f"- **Passed Checks:** {report.summary.get('passed_checks', 0)}",
            f"- **Failed Checks:** {report.summary.get('failed_checks', 0)}",
            f"- **Average RMSE:** {report.summary.get('average_rmse', 0.0):.4f}",
            f"- **Average Correlation:** {report.summary.get('average_correlation', 0.0):.4f}",
            "",
        ]

        if report.summary.get("failure_details"):
            lines.extend([
                "## Failed Acceptance Criteria",
                "",
            ])
            for failure in report.summary["failure_details"]:
                lines.append(f"- {failure}")
            lines.append("")

        if report.metrics:
            lines.extend([
                "## Detailed Metrics",
                "",
                "| Variable | RMSE | MAE | Max Error | Correlation | Bias |",
                "|----------|------|-----|-----------|-------------|------|",
            ])

            for var, metrics in report.metrics.items():
                lines.append(
                    f"| {var} | {metrics.rmse:.4f} | {metrics.mae:.4f} | "
                    f"{metrics.max_error:.4f} | {metrics.correlation:.4f} | "
                    f"{metrics.bias:.4f} |"
                )
            lines.append("")

        return "\n".join(lines)

    def generate_combined_report(
        self,
        validation_result: ValidationResult,
        comparison_report: ComparisonReport,
        output_format: str = "markdown",
    ) -> str:
        """Generate combined validation and comparison report.

        Args:
            validation_result: Validation result
            comparison_report: Comparison report
            output_format: Output format ('json', 'markdown')

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "json" if output_format == "json" else "md"
        filename = f"full_report_{comparison_report.mission_id}_{timestamp}.{ext}"
        filepath = self.output_dir / filename

        if output_format == "json":
            combined = {
                "validation": validation_result.to_dict(),
                "comparison": comparison_report.to_dict(),
                "timestamp": timestamp,
                "overall_status": validation_result.is_valid and comparison_report.passed,
            }

            with open(filepath, "w") as f:
                json.dump(combined, f, indent=2)

        elif output_format == "markdown":
            validation_md = self._generate_validation_markdown(validation_result)
            comparison_md = self._generate_comparison_markdown(comparison_report)

            overall_status = validation_result.is_valid and comparison_report.passed

            lines = [
                "# QuASIM Mission Data Integration Report",
                "",
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Overall Status:** {'✅ PASSED' if overall_status else '❌ FAILED'}",
                "",
                "---",
                "",
                validation_md,
                "",
                "---",
                "",
                comparison_md,
            ]

            with open(filepath, "w") as f:
                f.write("\n".join(lines))

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return str(filepath)

    def list_reports(self) -> list[str]:
        """List all generated reports.

        Returns:
            List of report file paths
        """
        reports = []
        for file in self.output_dir.glob("*"):
            if file.is_file():
                reports.append(str(file))
        return sorted(reports)
