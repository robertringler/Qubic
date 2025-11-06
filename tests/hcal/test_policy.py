"""Tests for policy validation."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import yaml

from quasim.hcal.policy import PolicyConfig, PolicyValidator


class TestPolicyConfig:
    """Tests for PolicyConfig class."""
    
    def test_policy_config_creation(self) -> None:
        """Test creating a policy config."""
        config = PolicyConfig(
            environment="DEV",
            allowed_backends=["cpu", "cuda"],
            limits={"max_qubits": 20},
        )
        
        assert config.environment == "DEV"
        assert config.allowed_backends == ["cpu", "cuda"]
        assert config.limits == {"max_qubits": 20}


class TestPolicyValidator:
    """Tests for PolicyValidator class."""
    
    def test_validator_init(self) -> None:
        """Test validator initialization."""
        validator = PolicyValidator()
        assert validator.policy is None
    
    def test_validator_with_config(self) -> None:
        """Test validator with configuration."""
        config = PolicyConfig(
            environment="LAB",
            allowed_backends=["cpu"],
            limits={"max_qubits": 10},
        )
        validator = PolicyValidator(config)
        assert validator.policy == config
    
    def test_from_file_valid(self, tmp_path: Path) -> None:
        """Test loading valid policy from file."""
        policy_data = {
            "environment": "DEV",
            "allowed_backends": ["cpu", "cuda"],
            "limits": {"max_qubits": 20, "max_circuits": 100},
        }
        
        policy_file = tmp_path / "policy.yaml"
        with open(policy_file, "w") as f:
            yaml.dump(policy_data, f)
        
        validator = PolicyValidator.from_file(policy_file)
        assert validator.policy.environment == "DEV"
        assert "cpu" in validator.policy.allowed_backends
        assert validator.policy.limits["max_qubits"] == 20
    
    def test_from_file_missing_file(self, tmp_path: Path) -> None:
        """Test loading from nonexistent file."""
        policy_file = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            PolicyValidator.from_file(policy_file)
    
    def test_from_file_invalid_environment(self, tmp_path: Path) -> None:
        """Test loading policy with invalid environment."""
        policy_data = {
            "environment": "INVALID",
            "allowed_backends": ["cpu"],
            "limits": {"max_qubits": 10},
        }
        
        policy_file = tmp_path / "policy.yaml"
        with open(policy_file, "w") as f:
            yaml.dump(policy_data, f)
        
        with pytest.raises(ValueError, match="Invalid environment"):
            PolicyValidator.from_file(policy_file)
    
    def test_from_file_missing_keys(self, tmp_path: Path) -> None:
        """Test loading policy with missing required keys."""
        policy_data = {
            "environment": "DEV",
            # missing allowed_backends and limits
        }
        
        policy_file = tmp_path / "policy.yaml"
        with open(policy_file, "w") as f:
            yaml.dump(policy_data, f)
        
        with pytest.raises(ValueError, match="Missing required policy key"):
            PolicyValidator.from_file(policy_file)
    
    def test_validate_backend_allowed(self) -> None:
        """Test validating allowed backend."""
        config = PolicyConfig(
            environment="DEV",
            allowed_backends=["cpu", "cuda"],
            limits={},
        )
        validator = PolicyValidator(config)
        
        assert validator.validate_backend("cpu") is True
        assert validator.validate_backend("cuda") is True
    
    def test_validate_backend_not_allowed(self) -> None:
        """Test validating disallowed backend."""
        config = PolicyConfig(
            environment="PROD",
            allowed_backends=["cpu"],
            limits={},
        )
        validator = PolicyValidator(config)
        
        assert validator.validate_backend("cuda") is False
    
    def test_validate_backend_no_policy(self) -> None:
        """Test validating backend with no policy."""
        validator = PolicyValidator()
        assert validator.validate_backend("any") is True
    
    def test_check_limits_within(self) -> None:
        """Test checking limits within bounds."""
        config = PolicyConfig(
            environment="DEV",
            allowed_backends=["cpu"],
            limits={"max_qubits": 20},
        )
        validator = PolicyValidator(config)
        
        assert validator.check_limits("max_qubits", 10) is True
        assert validator.check_limits("max_qubits", 20) is True
    
    def test_check_limits_exceeded(self) -> None:
        """Test checking limits when exceeded."""
        config = PolicyConfig(
            environment="PROD",
            allowed_backends=["cpu"],
            limits={"max_qubits": 10},
        )
        validator = PolicyValidator(config)
        
        assert validator.check_limits("max_qubits", 20) is False
    
    def test_check_limits_unknown_resource(self) -> None:
        """Test checking limits for unknown resource."""
        config = PolicyConfig(
            environment="DEV",
            allowed_backends=["cpu"],
            limits={"max_qubits": 20},
        )
        validator = PolicyValidator(config)
        
        # Unknown resources are allowed by default
        assert validator.check_limits("unknown_resource", 1000) is True
    
    def test_check_limits_no_policy(self) -> None:
        """Test checking limits with no policy."""
        validator = PolicyValidator()
        assert validator.check_limits("any", 1000) is True
