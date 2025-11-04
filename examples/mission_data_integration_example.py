"""Example script demonstrating mission data integration workflow.

This example shows how to:
1. Ingest SpaceX Falcon 9 flight telemetry data
2. Ingest NASA Orion/SLS mission telemetry
3. Run QuASIM simulations
4. Compare simulation predictions to real mission performance
5. Generate detailed performance reports
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from quasim.validation.mission_integration import MissionDataIntegrator


def example_spacex_falcon9():
    """Example: SpaceX Falcon 9 mission data integration."""
    print("\n" + "=" * 80)
    print("Example 1: SpaceX Falcon 9 Mission Data Integration")
    print("=" * 80 + "\n")

    # Create integrator for Falcon 9 missions
    integrator = MissionDataIntegrator(
        mission_type="falcon9",
        output_dir="reports/falcon9",
    )

    # Sample Falcon 9 telemetry data
    # In production, this would come from SpaceX telemetry streams
    falcon9_telemetry = [
        {
            "timestamp": 0.0,
            "vehicle_id": "Falcon9_B1067",
            "altitude": 100.0,
            "velocity": 50.0,
            "downrange": 0.0,
            "thrust": 7607.0,  # kN
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
        {
            "timestamp": 20.0,
            "vehicle_id": "Falcon9_B1067",
            "altitude": 5000.0,
            "velocity": 300.0,
            "downrange": 2.0,
            "thrust": 7607.0,
            "throttle": 95.0,
            "attitude_q": [0.998, 0.02, 0.0, 0.0],
            "angular_rates": [0.05, 0.0, 0.0],
            "guidance_mode": "NOMINAL",
            "isp": 282.0,
        },
        {
            "timestamp": 30.0,
            "vehicle_id": "Falcon9_B1067",
            "altitude": 10000.0,
            "velocity": 500.0,
            "downrange": 5.0,
            "thrust": 7607.0,
            "throttle": 90.0,
            "attitude_q": [0.997, 0.03, 0.0, 0.0],
            "angular_rates": [0.02, 0.0, 0.0],
            "guidance_mode": "NOMINAL",
            "isp": 282.0,
        },
    ]

    # Process mission data
    results = integrator.process_spacex_mission(
        mission_id="Falcon9_Starlink_6-25",
        telemetry_batch=falcon9_telemetry,
        output_format="markdown",
    )

    # Display results
    print("\n📊 Processing Results:")
    print(f"  - Mission ID: {results['mission_id']}")
    print(f"  - Data Points: {results['data_points']}")
    print(f"  - Validation: {'✅ PASSED' if results['validation']['is_valid'] else '❌ FAILED'}")

    if "comparison" in results:
        comparison = results["comparison"]
        print(f"  - Comparison: {'✅ PASSED' if comparison['passed'] else '⚠️  FAILED'}")
        print(f"  - Average RMSE: {comparison['summary']['average_rmse']:.2f}")
        print(f"  - Average Correlation: {comparison['summary']['average_correlation']:.4f}")

    if "report_path" in results:
        print(f"\n📄 Report generated: {results['report_path']}")

    return results


def example_nasa_orion():
    """Example: NASA Orion mission data integration."""
    print("\n" + "=" * 80)
    print("Example 2: NASA Orion Mission Data Integration")
    print("=" * 80 + "\n")

    # Create integrator for Orion missions
    integrator = MissionDataIntegrator(
        mission_type="orion",
        output_dir="reports/orion",
    )

    # Create sample NASA telemetry CSV file
    csv_path = Path("/tmp/orion_telemetry.csv")
    csv_content = """MET,vehicle,x,y,z,vx,vy,vz,GNC_mode
0.0,Orion,6678000.0,0.0,0.0,0.0,7500.0,0.0,NOMINAL
10.0,Orion,6677950.0,75000.0,0.0,-37.5,7500.0,0.0,NOMINAL
20.0,Orion,6677800.0,150000.0,0.0,-75.0,7499.0,0.0,NOMINAL
30.0,Orion,6677550.0,224950.0,0.0,-112.5,7498.0,0.0,NOMINAL
"""

    csv_path.write_text(csv_content)

    # Process mission data
    results = integrator.process_nasa_mission(
        mission_id="Artemis_I",
        log_file_path=str(csv_path),
        output_format="markdown",
    )

    # Display results
    print("\n📊 Processing Results:")
    print(f"  - Mission ID: {results['mission_id']}")
    print(f"  - Data Points: {results['data_points']}")
    print(f"  - Validation: {'✅ PASSED' if results['validation']['is_valid'] else '❌ FAILED'}")

    if "comparison" in results:
        comparison = results["comparison"]
        print(f"  - Comparison: {'✅ PASSED' if comparison['passed'] else '⚠️  FAILED'}")
        print(f"  - Average RMSE: {comparison['summary']['average_rmse']:.2f}")
        print(f"  - Average Correlation: {comparison['summary']['average_correlation']:.4f}")

    if "report_path" in results:
        print(f"\n📄 Report generated: {results['report_path']}")

    # Clean up
    csv_path.unlink()

    return results


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("QuASIM Mission Data Integration Examples")
    print("=" * 80)

    # Run SpaceX example
    falcon9_results = example_spacex_falcon9()

    # Run NASA example
    orion_results = example_nasa_orion()

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"\n✅ Successfully processed {len([falcon9_results, orion_results])} missions")
    print("\nGenerated reports:")
    if "report_path" in falcon9_results:
        print(f"  - Falcon 9: {falcon9_results['report_path']}")
    if "report_path" in orion_results:
        print(f"  - Orion: {orion_results['report_path']}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
