"""Tests for mission data validator."""

from __future__ import annotations

from quasim.validation.mission_validator import MissionDataValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_init_default(self):
        """Test default initialization."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")

        assert not result.is_valid
        assert result.error_count == 1
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")

        assert result.is_valid  # Warnings don't invalidate
        assert result.warning_count == 1
        assert "Test warning" in result.warnings

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = ValidationResult(is_valid=True)
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.metadata["key"] = "value"

        data = result.to_dict()
        assert data["is_valid"] is False
        assert data["error_count"] == 1
        assert data["warning_count"] == 1
        assert "Error 1" in data["errors"]
        assert "Warning 1" in data["warnings"]
        assert data["metadata"]["key"] == "value"


class TestMissionDataValidator:
    """Test MissionDataValidator."""

    def test_init_falcon9(self):
        """Test initialization for Falcon 9."""
        validator = MissionDataValidator(mission_type="falcon9")
        assert validator.mission_type == "falcon9"
        assert "required_fields" in validator._validation_rules

    def test_init_orion(self):
        """Test initialization for Orion."""
        validator = MissionDataValidator(mission_type="orion")
        assert validator.mission_type == "orion"

    def test_validate_completeness_success(self):
        """Test successful data completeness validation."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = {
            "timestamp": 100.0,
            "vehicle_id": "Falcon9_B1067",
            "altitude": 50000.0,
            "velocity": 2000.0,
        }

        result = validator.validate_data_completeness(data)
        assert result.is_valid
        assert result.error_count == 0

    def test_validate_completeness_missing_fields(self):
        """Test data completeness validation with missing fields."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = {
            "timestamp": 100.0,
            # Missing vehicle_id, altitude, velocity
        }

        result = validator.validate_data_completeness(data)
        assert not result.is_valid
        assert result.error_count >= 1

    def test_validate_physical_ranges_falcon9_success(self):
        """Test physical range validation for Falcon 9."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = {
            "altitude": 100000.0,  # 100 km
            "velocity": 5000.0,  # 5 km/s
            "throttle": 85.0,
        }

        result = validator.validate_physical_ranges(data)
        assert result.is_valid

    def test_validate_physical_ranges_falcon9_out_of_range(self):
        """Test physical range validation with out-of-range values."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = {
            "altitude": 600000.0,  # Above 500 km limit
            "velocity": 15000.0,  # Above 12 km/s limit
        }

        result = validator.validate_physical_ranges(data)
        assert not result.is_valid
        assert result.error_count >= 1

    def test_validate_physical_ranges_orion_success(self):
        """Test physical range validation for Orion."""
        validator = MissionDataValidator(mission_type="orion")
        data = {
            "state_vector": [
                7000000.0,  # x (m)
                0.0,  # y (m)
                0.0,  # z (m)
                0.0,  # vx (m/s)
                7500.0,  # vy (m/s)
                0.0,  # vz (m/s)
            ],
        }

        result = validator.validate_physical_ranges(data)
        assert result.is_valid

    def test_validate_temporal_consistency_success(self):
        """Test temporal consistency validation with monotonic timestamps."""
        validator = MissionDataValidator(mission_type="falcon9")
        data_sequence = [
            {"timestamp": 0.0, "altitude": 0.0},
            {"timestamp": 1.0, "altitude": 100.0},
            {"timestamp": 2.0, "altitude": 200.0},
        ]

        result = validator.validate_temporal_consistency(data_sequence)
        assert result.is_valid

    def test_validate_temporal_consistency_non_monotonic(self):
        """Test temporal consistency validation with non-monotonic timestamps."""
        validator = MissionDataValidator(mission_type="falcon9")
        data_sequence = [
            {"timestamp": 0.0, "altitude": 0.0},
            {"timestamp": 2.0, "altitude": 200.0},
            {"timestamp": 1.0, "altitude": 100.0},  # Goes backwards
        ]

        result = validator.validate_temporal_consistency(data_sequence)
        assert not result.is_valid
        assert result.error_count >= 1

    def test_validate_full_success(self):
        """Test full validation with valid data."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = [
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

        result = validator.validate_full(data)
        assert result.is_valid
        assert result.metadata["data_points_validated"] == 2

    def test_validate_full_single_point(self):
        """Test full validation with single data point."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = {
            "timestamp": 0.0,
            "vehicle_id": "Falcon9_B1067",
            "altitude": 1000.0,
            "velocity": 100.0,
        }

        result = validator.validate_full(data)
        assert result.is_valid

    def test_validate_full_with_errors(self):
        """Test full validation with erroneous data."""
        validator = MissionDataValidator(mission_type="falcon9")
        data = [
            {
                "timestamp": 0.0,
                # Missing required fields
                "altitude": 600000.0,  # Out of range
            },
        ]

        result = validator.validate_full(data)
        assert not result.is_valid
        assert result.error_count > 0
