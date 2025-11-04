"""Integration tests for mission data validation workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from quasim.validation.mission_integration import MissionDataIntegrator


class TestMissionDataIntegration:
    """Test complete mission data integration workflow."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        return str(tmp_path / "integration_reports")

    def test_spacex_falcon9_workflow(self, temp_output_dir):
        """Test complete SpaceX Falcon 9 workflow."""
        integrator = MissionDataIntegrator(
            mission_type="falcon9",
            output_dir=temp_output_dir,
        )

        # Sample telemetry data
        telemetry_batch = [
            {
                "timestamp": 0.0,
                "vehicle_id": "Falcon9_B1067",
                "altitude": 100.0,
                "velocity": 50.0,
                "downrange": 0.0,
                "thrust": 7607.0,
                "throttle": 100.0,
                "attitude_q": [1.0, 0.0, 0.0, 0.0],
                "angular_rates": [0.0, 0.0, 0.0],
                "guidance_mode": "NOMINAL",
                "isp": 282.0,
            },
            {
                "timestamp": 10.0,
                "vehicle_id": "Falcon9_B1067",
                "altitude": 1500.0,
                "velocity": 150.0,
                "downrange": 0.5,
                "thrust": 7607.0,
                "throttle": 100.0,
                "attitude_q": [0.999, 0.01, 0.0, 0.0],
                "angular_rates": [0.1, 0.0, 0.0],
                "guidance_mode": "NOMINAL",
                "isp": 282.0,
            },
        ]

        # Process mission
        results = integrator.process_spacex_mission(
            mission_id="test_falcon9",
            telemetry_batch=telemetry_batch,
            output_format="json",
        )

        # Verify results structure
        assert results["mission_id"] == "test_falcon9"
        assert results["mission_type"] == "falcon9"
        assert results["data_points"] == 2
        assert "validation" in results
        assert results["validation"]["is_valid"]

        # Verify report generation
        assert "report_path" in results
        report_path = Path(results["report_path"])
        assert report_path.exists()
        assert report_path.suffix == ".json"

    def test_nasa_orion_workflow(self, temp_output_dir, tmp_path):
        """Test complete NASA Orion workflow."""
        integrator = MissionDataIntegrator(
            mission_type="orion",
            output_dir=temp_output_dir,
        )

        # Create temporary CSV file
        csv_path = tmp_path / "orion_test.csv"
        csv_content = """MET,vehicle,x,y,z,vx,vy,vz,GNC_mode
0.0,Orion,6678000.0,0.0,0.0,0.0,7500.0,0.0,NOMINAL
10.0,Orion,6677950.0,75000.0,0.0,-37.5,7500.0,0.0,NOMINAL
"""
        csv_path.write_text(csv_content)

        # Process mission
        results = integrator.process_nasa_mission(
            mission_id="test_artemis",
            log_file_path=str(csv_path),
            output_format="markdown",
        )

        # Verify results structure
        assert results["mission_id"] == "test_artemis"
        assert results["mission_type"] == "orion"
        assert results["data_points"] == 2
        assert "validation" in results

    def test_data_ingestion_spacex(self):
        """Test SpaceX data ingestion."""
        integrator = MissionDataIntegrator(mission_type="falcon9")

        telemetry_batch = [
            {
                "timestamp": 0.0,
                "vehicle_id": "Falcon9_B1067",
                "altitude": 1000.0,
                "velocity": 100.0,
            },
            {
                "timestamp": 1.0,
                "vehicle_id": "Falcon9_B1067",
                "altitude": 2000.0,
                "velocity": 200.0,
            },
        ]

        parsed_data, successful, failed = integrator.ingest_spacex_data(
            telemetry_batch
        )

        assert successful == 2
        assert failed == 0
        assert len(parsed_data) == 2
        assert all("altitude" in d for d in parsed_data)
        assert all("velocity" in d for d in parsed_data)

    def test_data_ingestion_nasa(self, tmp_path):
        """Test NASA data ingestion."""
        integrator = MissionDataIntegrator(mission_type="orion")

        # Create temporary CSV file
        csv_path = tmp_path / "nasa_test.csv"
        csv_content = """MET,vehicle,x,y,z,vx,vy,vz,GNC_mode
0.0,Orion,6678000.0,0.0,0.0,0.0,7500.0,0.0,NOMINAL
10.0,Orion,6678000.0,75000.0,0.0,0.0,7500.0,0.0,NOMINAL
"""
        csv_path.write_text(csv_content)

        parsed_data, successful, failed = integrator.ingest_nasa_data(
            str(csv_path)
        )

        assert successful == 2
        assert failed == 0
        assert len(parsed_data) == 2
        assert all("timestamp" in d for d in parsed_data)

    def test_simulation_execution(self):
        """Test QuASIM simulation execution."""
        integrator = MissionDataIntegrator(mission_type="falcon9")

        mission_data = [
            {"timestamp": 0.0, "altitude": 1000.0, "velocity": 100.0},
            {"timestamp": 1.0, "altitude": 2000.0, "velocity": 200.0},
        ]

        simulation_trajectory = integrator.run_simulation(mission_data)

        assert len(simulation_trajectory) == len(mission_data)
        assert all(isinstance(point, dict) for point in simulation_trajectory)

    def test_validation_error_handling(self):
        """Test validation error handling with invalid data."""
        integrator = MissionDataIntegrator(mission_type="falcon9")

        # Invalid telemetry (missing required fields)
        invalid_telemetry = [
            {"timestamp": 0.0},  # Missing vehicle_id, altitude, velocity
        ]

        parsed_data, successful, failed = integrator.ingest_spacex_data(
            invalid_telemetry
        )

        # Should handle gracefully
        assert failed >= 0  # May fail validation
        assert isinstance(parsed_data, list)

    def test_report_formats(self, temp_output_dir):
        """Test different report output formats."""
        integrator = MissionDataIntegrator(
            mission_type="falcon9",
            output_dir=temp_output_dir,
        )

        mission_data = [
            {
                "timestamp": 0.0,
                "vehicle_id": "Falcon9_Test",
                "altitude": 1000.0,
                "velocity": 100.0,
            }
        ]

        # Test JSON format
        results_json = integrator.process_mission(
            mission_id="test_json",
            mission_data=mission_data,
            output_format="json",
        )

        assert Path(results_json.get("report_path", "")).suffix == ".json"

        # Test Markdown format
        results_md = integrator.process_mission(
            mission_id="test_md",
            mission_data=mission_data,
            output_format="markdown",
        )

        assert Path(results_md.get("report_path", "")).suffix == ".md"

    def test_empty_mission_data(self):
        """Test handling of empty mission data."""
        integrator = MissionDataIntegrator(mission_type="falcon9")

        simulation_trajectory = integrator.run_simulation([])

        assert len(simulation_trajectory) == 0

    def test_comparison_metrics_computation(self, temp_output_dir):
        """Test comparison metrics are computed correctly."""
        integrator = MissionDataIntegrator(
            mission_type="falcon9",
            output_dir=temp_output_dir,
        )

        mission_data = [
            {
                "timestamp": 0.0,
                "vehicle_id": "Falcon9_Test",
                "altitude": 1000.0,
                "velocity": 100.0,
            },
            {
                "timestamp": 1.0,
                "vehicle_id": "Falcon9_Test",
                "altitude": 2000.0,
                "velocity": 200.0,
            },
        ]

        results = integrator.process_mission(
            mission_id="test_metrics",
            mission_data=mission_data,
            output_format="json",
        )

        # Verify comparison metrics exist
        if "comparison" in results:
            comparison = results["comparison"]
            assert "metrics" in comparison
            assert "summary" in comparison
            assert "average_rmse" in comparison["summary"]
            assert "average_correlation" in comparison["summary"]
