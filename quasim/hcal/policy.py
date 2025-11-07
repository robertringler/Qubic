"""Policy enforcement and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


@dataclass
class PolicyConfig:
    """Policy configuration.

    Attributes:
        environment: Environment type (DEV, LAB, PROD)
        allowed_backends: List of allowed compute backends
        limits: Resource limits
        raw_config: Raw configuration dictionary
    """

    environment: str
    allowed_backends: list[str]
    limits: dict[str, Any]
    raw_config: dict[str, Any] = field(default_factory=dict)


class PolicyValidator:
    """Validates and enforces hardware control policies."""

    def __init__(self, policy_config: PolicyConfig | None = None) -> None:
        """Initialize policy validator.

        Args:
            policy_config: Policy configuration
        """
        self.policy = policy_config

    @classmethod
    def from_file(cls, policy_path: Path) -> PolicyValidator:
        """Load policy from YAML file.

        Args:
            policy_path: Path to policy YAML file

        Returns:
            PolicyValidator instance

        Raises:
            FileNotFoundError: If policy file doesn't exist
            ValueError: If policy is invalid
        """
        if not policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_path}")

        with open(policy_path) as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError(f"Policy file is empty or invalid: {policy_path}")

        cls._validate_config(config)

        policy = PolicyConfig(
            environment=config["environment"],
            allowed_backends=config["allowed_backends"],
            limits=config["limits"],
            raw_config=config,
        )

        return cls(policy)

    @staticmethod
    def _validate_config(config: dict[str, Any]) -> None:
        """Validate policy configuration.

        Args:
            config: Configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = ["environment", "allowed_backends", "limits"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required policy key: {key}")

        valid_environments = ["DEV", "LAB", "PROD"]
        if config["environment"] not in valid_environments:
            raise ValueError(
                f"Invalid environment: {config['environment']}. Must be one of {valid_environments}"
            )

    def validate_backend(self, backend: str) -> bool:
        """Validate if backend is allowed.

        Args:
            backend: Backend name to validate

        Returns:
            True if backend is allowed
        """
        if not self.policy:
            return True

        return backend in self.policy.allowed_backends

    def check_limits(self, resource: str, value: int) -> bool:
        """Check if resource value is within limits.

        Args:
            resource: Resource name
            value: Resource value to check

        Returns:
            True if within limits
        """
        if not self.policy or resource not in self.policy.limits:
            return True

        limit = int(self.policy.limits[resource])
        return value <= limit
