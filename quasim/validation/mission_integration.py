"""Mission data integration and simulation comparison engine."""

from __future__ import annotations

from typing import Any

from telemetry_api import NASATelemetryAdapter, SpaceXTelemetryAdapter

from ..dtwin.simulation import DigitalTwin
from .mission_validator import MissionDataValidator
from .performance_comparison import PerformanceComparator
from .report_generator import ReportGenerator


class MissionDataIntegrator:
    """Integrates real mission data with QuASIM simulations.

    Orchestrates the complete workflow of:
    1. Ingesting real mission telemetry
    2. Validating data quality and completeness
    3. Running QuASIM simulations with equivalent parameters
    4. Comparing simulation predictions to actual mission performance
    5. Generating detailed performance reports
    """

    def __init__(
        self,
        mission_type: str = "falcon9",
        output_dir: str = "reports",
    ):
        """Initialize mission data integrator.

        Args:
            mission_type: Type of mission ('falcon9', 'orion', 'sls')
            output_dir: Directory for output reports
        """
        self.mission_type = mission_type
        self.validator = MissionDataValidator(mission_type=mission_type)
        self.comparator = PerformanceComparator()
        self.report_generator = ReportGenerator(output_dir=output_dir)

        # Initialize telemetry adapters
        if mission_type == "falcon9":
            self.telemetry_adapter = SpaceXTelemetryAdapter()
        elif mission_type in ["orion", "sls"]:
            self.telemetry_adapter = NASATelemetryAdapter()
        else:
            raise ValueError(f"Unsupported mission type: {mission_type}")

    def ingest_spacex_data(
        self,
        telemetry_batch: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Ingest SpaceX Falcon 9 telemetry data.

        Args:
            telemetry_batch: List of raw telemetry dictionaries

        Returns:
            Tuple of (parsed_data, successful_count, failed_count)
        """
        if not isinstance(self.telemetry_adapter, SpaceXTelemetryAdapter):
            raise ValueError("Mission type must be 'falcon9' for SpaceX data")

        parsed_data = []
        successful, failed, errors = self.telemetry_adapter.ingest_batch(telemetry_batch)

        # Parse and store successful records
        for raw_data in telemetry_batch:
            try:
                telemetry = self.telemetry_adapter.parse_telemetry(raw_data)
                is_valid, _ = self.telemetry_adapter.validate_schema(telemetry)

                if is_valid:
                    # Convert to QuASIM format
                    parsed = {
                        "timestamp": telemetry.timestamp,
                        "vehicle_id": telemetry.vehicle_id,
                        "altitude": telemetry.ascent_data.get("altitude_m", 0.0),
                        "velocity": telemetry.ascent_data.get("velocity_mps", 0.0),
                        "downrange": telemetry.ascent_data.get("downrange_km", 0.0),
                        "thrust": telemetry.engine_data.get("thrust_kn", 0.0),
                        "throttle": telemetry.engine_data.get("throttle_pct", 100.0),
                    }
                    parsed_data.append(parsed)
            except Exception:
                continue

        return parsed_data, successful, failed

    def ingest_nasa_data(
        self,
        log_file_path: str,
    ) -> tuple[list[dict[str, Any]], int, int]:
        """Ingest NASA Orion/SLS telemetry data from log file.

        Args:
            log_file_path: Path to NASA telemetry log file

        Returns:
            Tuple of (parsed_data, successful_count, failed_count)
        """
        if not isinstance(self.telemetry_adapter, NASATelemetryAdapter):
            raise ValueError("Mission type must be 'orion' or 'sls' for NASA data")

        # Ingest log file
        successful, failed, errors = self.telemetry_adapter.ingest_log_file(log_file_path)

        # Parse log file and convert to QuASIM format
        parsed_data = []
        try:
            with open(log_file_path) as f:
                lines = f.readlines()

            # Skip header if present
            start_idx = 1 if lines and "MET" in lines[0] else 0

            for line in lines[start_idx:]:
                try:
                    telemetry = self.telemetry_adapter.parse_csv_log(line)
                    is_valid, _ = self.telemetry_adapter.validate_schema(telemetry)

                    if is_valid:
                        parsed = self.telemetry_adapter.export_quasim_format(telemetry)
                        parsed_data.append(parsed)
                except Exception:
                    continue
        except Exception:
            pass

        return parsed_data, successful, failed

    def run_simulation(
        self,
        mission_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Run QuASIM simulation based on mission parameters.

        Args:
            mission_data: Parsed mission telemetry data

        Returns:
            Simulated trajectory matching mission timeline
        """
        if not mission_data:
            return []

        # Create digital twin for aerospace simulation
        twin = DigitalTwin(
            twin_id=f"sim_{self.mission_type}",
            system_type="aerospace",
            parameters={
                "mission_type": self.mission_type,
                "initial_state": mission_data[0],
            },
        )

        # Initialize with first data point
        twin.update_state(mission_data[0])

        # Simulate forward to match real data timeline
        simulation_trajectory = []

        for i, real_point in enumerate(mission_data):
            # Evolve simulation
            if i > 0:
                time_field = "timestamp" if "timestamp" in real_point else "timestamp"
                prev_time = mission_data[i-1].get(time_field, 0.0)
                curr_time = real_point.get(time_field, 0.0)
                delta_t = curr_time - prev_time

                # Simulate one step forward
                if delta_t > 0:
                    trajectory = twin.simulate_forward(time_steps=1, delta_t=delta_t)
                    if trajectory:
                        simulation_trajectory.append(trajectory[0])
                else:
                    simulation_trajectory.append(twin.state_manager.get_current_state())
            else:
                simulation_trajectory.append(real_point.copy())

        return simulation_trajectory

    def process_mission(
        self,
        mission_id: str,
        mission_data: list[dict[str, Any]],
        output_format: str = "markdown",
    ) -> dict[str, Any]:
        """Process complete mission data integration workflow.

        Args:
            mission_id: Mission identifier
            mission_data: Parsed mission telemetry data
            output_format: Report output format ('json', 'markdown')

        Returns:
            Dictionary with validation, simulation, and comparison results
        """
        results = {
            "mission_id": mission_id,
            "mission_type": self.mission_type,
            "data_points": len(mission_data),
        }

        # Step 1: Validate mission data
        print(f"Validating mission data for {mission_id}...")
        validation_result = self.validator.validate_full(mission_data)
        results["validation"] = validation_result.to_dict()

        if not validation_result.is_valid:
            print(f"⚠️  Validation failed with {validation_result.error_count} errors")
            # Generate validation report
            report_path = self.report_generator.generate_validation_report(
                validation_result,
                output_format=output_format,
            )
            results["validation_report"] = report_path
            return results

        print("✅ Validation passed")

        # Step 2: Run QuASIM simulation
        print("Running QuASIM simulation...")
        simulation_trajectory = self.run_simulation(mission_data)
        results["simulation_points"] = len(simulation_trajectory)

        # Step 3: Compare simulation to real data
        print("Comparing simulation to mission data...")
        comparison_report = self.comparator.generate_report(
            mission_id=mission_id,
            simulation_id=f"quasim_{mission_id}",
            simulation_trajectory=simulation_trajectory,
            real_trajectory=mission_data,
        )
        results["comparison"] = comparison_report.to_dict()

        if comparison_report.passed:
            print("✅ Comparison passed acceptance criteria")
        else:
            print("⚠️  Comparison failed acceptance criteria")

        # Step 4: Generate comprehensive report
        print("Generating performance report...")
        report_path = self.report_generator.generate_combined_report(
            validation_result,
            comparison_report,
            output_format=output_format,
        )
        results["report_path"] = report_path

        print(f"📊 Report generated: {report_path}")

        return results

    def process_spacex_mission(
        self,
        mission_id: str,
        telemetry_batch: list[dict[str, Any]],
        output_format: str = "markdown",
    ) -> dict[str, Any]:
        """Process SpaceX Falcon 9 mission data.

        Args:
            mission_id: Mission identifier
            telemetry_batch: Raw SpaceX telemetry data
            output_format: Report output format

        Returns:
            Processing results and report paths
        """
        print(f"Processing SpaceX mission: {mission_id}")
        print(f"Ingesting {len(telemetry_batch)} telemetry records...")

        parsed_data, successful, failed = self.ingest_spacex_data(telemetry_batch)
        print(f"✅ Ingested {successful} records successfully ({failed} failed)")

        return self.process_mission(mission_id, parsed_data, output_format)

    def process_nasa_mission(
        self,
        mission_id: str,
        log_file_path: str,
        output_format: str = "markdown",
    ) -> dict[str, Any]:
        """Process NASA Orion/SLS mission data.

        Args:
            mission_id: Mission identifier
            log_file_path: Path to NASA telemetry log
            output_format: Report output format

        Returns:
            Processing results and report paths
        """
        print(f"Processing NASA mission: {mission_id}")
        print(f"Ingesting data from: {log_file_path}")

        parsed_data, successful, failed = self.ingest_nasa_data(log_file_path)
        print(f"✅ Ingested {successful} records successfully ({failed} failed)")

        return self.process_mission(mission_id, parsed_data, output_format)
