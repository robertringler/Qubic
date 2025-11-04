"""Mission data validation for real telemetry data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of mission data validation.

    Attributes:
        is_valid: Whether validation passed
        error_count: Number of validation errors
        warning_count: Number of validation warnings
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional validation metadata
    """

    is_valid: bool
    error_count: int = 0
    warning_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.errors.append(message)
        self.error_count += 1
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)
        self.warning_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


class MissionDataValidator:
    """Validator for real mission telemetry data.

    Validates mission data for completeness, consistency, and physical plausibility
    before comparison with QuASIM simulations.
    """

    def __init__(self, mission_type: str = "falcon9"):
        """Initialize mission data validator.

        Args:
            mission_type: Type of mission ('falcon9', 'orion', 'sls')
        """
        self.mission_type = mission_type
        self._validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> dict[str, Any]:
        """Load validation rules for mission type."""
        rules = {
            "falcon9": {
                "required_fields": ["timestamp", "vehicle_id", "altitude", "velocity"],
                "altitude_range": (0, 500_000),  # meters
                "velocity_range": (0, 12_000),  # m/s
                "throttle_range": (40, 100),  # percent
            },
            "orion": {
                "required_fields": ["met", "vehicle_system", "state_vector"],
                "position_range": (6_000_000, 50_000_000),  # meters
                "velocity_range": (0, 15_000),  # m/s
            },
            "sls": {
                "required_fields": ["met", "vehicle_system", "state_vector"],
                "position_range": (6_000_000, 50_000_000),  # meters
                "velocity_range": (0, 15_000),  # m/s
            },
        }
        return rules.get(self.mission_type, rules["falcon9"])

    def validate_data_completeness(self, data: dict[str, Any]) -> ValidationResult:
        """Validate that required fields are present.

        Args:
            data: Mission data dictionary

        Returns:
            ValidationResult with completeness check results
        """
        result = ValidationResult(is_valid=True)

        required = self._validation_rules.get("required_fields", [])
        for field_name in required:
            if field_name not in data:
                result.add_error(f"Missing required field: {field_name}")

        result.metadata["checked_fields"] = required
        return result

    def validate_physical_ranges(self, data: dict[str, Any]) -> ValidationResult:
        """Validate that values are within physical ranges.

        Args:
            data: Mission data dictionary

        Returns:
            ValidationResult with range check results
        """
        result = ValidationResult(is_valid=True)

        # Validate altitude for Falcon 9
        if self.mission_type == "falcon9":
            if "altitude" in data:
                altitude = data["altitude"]
                min_alt, max_alt = self._validation_rules["altitude_range"]
                if not (min_alt <= altitude <= max_alt):
                    result.add_error(
                        f"Altitude {altitude}m out of range [{min_alt}, {max_alt}]"
                    )

            if "velocity" in data:
                velocity = data["velocity"]
                min_vel, max_vel = self._validation_rules["velocity_range"]
                if not (min_vel <= velocity <= max_vel):
                    result.add_error(
                        f"Velocity {velocity}m/s out of range [{min_vel}, {max_vel}]"
                    )

            if "throttle" in data:
                throttle = data["throttle"]
                min_thr, max_thr = self._validation_rules["throttle_range"]
                if not (min_thr <= throttle <= max_thr):
                    result.add_warning(
                        f"Throttle {throttle}% outside typical range [{min_thr}, {max_thr}]"
                    )

        # Validate state vector for Orion/SLS
        elif self.mission_type in ["orion", "sls"]:
            if "state_vector" in data:
                state = data["state_vector"]
                if len(state) >= 3:
                    pos_mag = (state[0]**2 + state[1]**2 + state[2]**2) ** 0.5
                    min_pos, max_pos = self._validation_rules["position_range"]
                    if not (min_pos <= pos_mag <= max_pos):
                        result.add_error(
                            f"Position magnitude {pos_mag/1000:.1f}km out of range "
                            f"[{min_pos/1000:.1f}, {max_pos/1000:.1f}]km"
                        )

                if len(state) >= 6:
                    vel_mag = (state[3]**2 + state[4]**2 + state[5]**2) ** 0.5
                    min_vel, max_vel = self._validation_rules["velocity_range"]
                    if not (min_vel <= vel_mag <= max_vel):
                        result.add_error(
                            f"Velocity magnitude {vel_mag:.1f}m/s out of range "
                            f"[{min_vel}, {max_vel}]m/s"
                        )

        return result

    def validate_temporal_consistency(
        self, data_sequence: list[dict[str, Any]]
    ) -> ValidationResult:
        """Validate temporal consistency across data sequence.

        Args:
            data_sequence: Ordered sequence of mission data points

        Returns:
            ValidationResult with temporal consistency check results
        """
        result = ValidationResult(is_valid=True)

        if len(data_sequence) < 2:
            result.add_warning("Insufficient data points for temporal validation")
            return result

        # Check timestamp monotonicity
        time_field = "timestamp" if self.mission_type == "falcon9" else "met"

        for i in range(1, len(data_sequence)):
            if time_field in data_sequence[i] and time_field in data_sequence[i-1]:
                t_curr = data_sequence[i][time_field]
                t_prev = data_sequence[i-1][time_field]

                if t_curr <= t_prev:
                    result.add_error(
                        f"Non-monotonic timestamps at index {i}: "
                        f"{t_prev} -> {t_curr}"
                    )

        result.metadata["data_points"] = len(data_sequence)
        return result

    def validate_full(
        self, data: dict[str, Any] | list[dict[str, Any]]
    ) -> ValidationResult:
        """Run full validation suite on mission data.

        Args:
            data: Mission data (single point or sequence)

        Returns:
            ValidationResult with all validation results
        """
        result = ValidationResult(is_valid=True)

        # Handle single data point or sequence
        data_list = [data] if isinstance(data, dict) else data

        # Validate each data point
        for i, data_point in enumerate(data_list):
            completeness = self.validate_data_completeness(data_point)
            if not completeness.is_valid:
                for error in completeness.errors:
                    result.add_error(f"Point {i}: {error}")

            ranges = self.validate_physical_ranges(data_point)
            if not ranges.is_valid:
                for error in ranges.errors:
                    result.add_error(f"Point {i}: {error}")
            for warning in ranges.warnings:
                result.add_warning(f"Point {i}: {warning}")

        # Validate temporal consistency for sequences
        if len(data_list) > 1:
            temporal = self.validate_temporal_consistency(data_list)
            result.errors.extend(temporal.errors)
            result.warnings.extend(temporal.warnings)
            if not temporal.is_valid:
                result.is_valid = False

        result.error_count = len(result.errors)
        result.warning_count = len(result.warnings)
        result.metadata["mission_type"] = self.mission_type
        result.metadata["data_points_validated"] = len(data_list)

        return result
