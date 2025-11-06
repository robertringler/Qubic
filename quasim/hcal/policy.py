"""Policy engine for HCAL - declarative YAML-based policy configuration."""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class Environment(Enum):
    """Environment types for policy enforcement."""

    DEV = "dev"
    LAB = "lab"
    PROD = "prod"


@dataclass
class DeviceLimits:
    """Hardware limits for devices."""

    max_power_watts: Optional[float] = None
    max_temp_celsius: Optional[float] = None
    max_voltage_volts: Optional[float] = None
    max_clock_mhz: Optional[float] = None
    min_power_watts: Optional[float] = None
    min_temp_celsius: Optional[float] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    commands_per_minute: int = 30
    window_seconds: int = 60


@dataclass
class ApprovalGate:
    """Approval gate configuration."""

    required: bool = False
    min_approvers: int = 0
    methods: List[str] = field(default_factory=list)


@dataclass
class PolicyConfig:
    """Complete policy configuration."""

    environment: Environment
    device_allowlist: List[str]
    backend_restrictions: List[str]
    device_limits: Dict[str, DeviceLimits]
    rate_limit: RateLimitConfig
    approval_gate: ApprovalGate
    dry_run_default: bool = True


class PolicyEngine:
    """Policy engine for HCAL operations."""

    def __init__(self, policy_path: Optional[Path] = None):
        """Initialize policy engine.

        Args:
            policy_path: Path to policy YAML file. If None, uses default policy.
        """
        self.policy_path = policy_path
        self.policy: Optional[PolicyConfig] = None
        self._command_history: List[float] = []

        if policy_path:
            self.load_policy(policy_path)
        else:
            self._load_default_policy()

    def _load_default_policy(self):
        """Load default restrictive policy."""
        self.policy = PolicyConfig(
            environment=Environment.DEV,
            device_allowlist=["*"],
            backend_restrictions=[],
            device_limits={},
            rate_limit=RateLimitConfig(),
            approval_gate=ApprovalGate(),
            dry_run_default=True,
        )

    def load_policy(self, policy_path: Path):
        """Load policy from YAML file.

        Args:
            policy_path: Path to policy YAML file.

        Raises:
            ValueError: If policy is invalid.
        """
        with open(policy_path) as f:
            data = yaml.safe_load(f)

        self._validate_schema(data)
        self.policy = self._parse_policy(data)

    def _validate_schema(self, data: Dict[str, Any]):
        """Validate policy schema.

        Args:
            data: Policy data dictionary.

        Raises:
            ValueError: If schema is invalid.
        """
        required_fields = ["environment", "device_allowlist", "backend_restrictions"]
        for field_name in required_fields:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        if data["environment"] not in ["dev", "lab", "prod"]:
            raise ValueError(f"Invalid environment: {data['environment']}")

    def _parse_policy(self, data: Dict[str, Any]) -> PolicyConfig:
        """Parse policy data into PolicyConfig.

        Args:
            data: Policy data dictionary.

        Returns:
            PolicyConfig instance.
        """
        # Parse device limits
        device_limits = {}
        for device, limits in data.get("device_limits", {}).items():
            device_limits[device] = DeviceLimits(
                max_power_watts=limits.get("max_power_watts"),
                max_temp_celsius=limits.get("max_temp_celsius"),
                max_voltage_volts=limits.get("max_voltage_volts"),
                max_clock_mhz=limits.get("max_clock_mhz"),
                min_power_watts=limits.get("min_power_watts"),
                min_temp_celsius=limits.get("min_temp_celsius"),
            )

        # Parse rate limit
        rate_limit_data = data.get("rate_limit", {})
        rate_limit = RateLimitConfig(
            commands_per_minute=rate_limit_data.get("commands_per_minute", 30),
            window_seconds=rate_limit_data.get("window_seconds", 60),
        )

        # Parse approval gate
        approval_data = data.get("approval_gate", {})
        approval_gate = ApprovalGate(
            required=approval_data.get("required", False),
            min_approvers=approval_data.get("min_approvers", 0),
            methods=approval_data.get("methods", []),
        )

        return PolicyConfig(
            environment=Environment(data["environment"]),
            device_allowlist=data["device_allowlist"],
            backend_restrictions=data["backend_restrictions"],
            device_limits=device_limits,
            rate_limit=rate_limit,
            approval_gate=approval_gate,
            dry_run_default=data.get("dry_run_default", True),
        )

    def check_device_allowed(self, device_id: str) -> bool:
        """Check if device is allowed by policy.

        Args:
            device_id: Device identifier.

        Returns:
            True if device is allowed.
        """
        if not self.policy:
            return False

        if "*" in self.policy.device_allowlist:
            return True

        return device_id in self.policy.device_allowlist

    def check_backend_allowed(self, backend: str) -> bool:
        """Check if backend is allowed by policy.

        Args:
            backend: Backend name.

        Returns:
            True if backend is allowed.
        """
        if not self.policy:
            return False

        return backend not in self.policy.backend_restrictions

    def check_limits(self, device_id: str, setpoint: Dict[str, Any]) -> bool:
        """Check if setpoint is within limits.

        Args:
            device_id: Device identifier.
            setpoint: Setpoint dictionary.

        Returns:
            True if setpoint is within limits.
        """
        if not self.policy:
            return False

        limits = self.policy.device_limits.get(device_id)
        if not limits:
            # No limits defined, allow
            return True

        # Check power limits
        power_key = None
        if "power_watts" in setpoint:
            power_key = "power_watts"
        elif "power_limit_watts" in setpoint:
            power_key = "power_limit_watts"

        if power_key:
            power = setpoint[power_key]
            if limits.max_power_watts and power > limits.max_power_watts:
                return False
            if limits.min_power_watts and power < limits.min_power_watts:
                return False

        # Check temperature limits
        if "temp_celsius" in setpoint:
            temp = setpoint["temp_celsius"]
            if limits.max_temp_celsius and temp > limits.max_temp_celsius:
                return False
            if limits.min_temp_celsius and temp < limits.min_temp_celsius:
                return False

        # Check voltage limits
        if "voltage_volts" in setpoint:
            voltage = setpoint["voltage_volts"]
            if limits.max_voltage_volts and voltage > limits.max_voltage_volts:
                return False

        # Check clock limits
        if "clock_mhz" in setpoint:
            clock = setpoint["clock_mhz"]
            if limits.max_clock_mhz and clock > limits.max_clock_mhz:
                return False

        return True

    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded.

        Returns:
            True if rate limit is not exceeded.
        """
        if not self.policy:
            return False

        now = time.time()
        window_start = now - self.policy.rate_limit.window_seconds

        # Remove old entries
        self._command_history = [ts for ts in self._command_history if ts >= window_start]

        # Check rate
        if len(self._command_history) >= self.policy.rate_limit.commands_per_minute:
            return False

        # Record this check
        self._command_history.append(now)
        return True

    def check_approval(self, operation: str) -> bool:
        """Check if operation has required approval.

        Args:
            operation: Operation description.

        Returns:
            True if approval requirements are met.
        """
        if not self.policy:
            return False

        if not self.policy.approval_gate.required:
            return True

        # In a real implementation, this would check an approval database
        # For now, we return False if approval is required
        return False

    def get_environment(self) -> Environment:
        """Get current environment.

        Returns:
            Current environment.
        """
        if not self.policy:
            return Environment.DEV
        return self.policy.environment

    def is_dry_run_default(self) -> bool:
        """Check if dry-run is default.

        Returns:
            True if dry-run is default.
        """
        if not self.policy:
            return True
        return self.policy.dry_run_default
