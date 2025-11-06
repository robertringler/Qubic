"""Command-line interface for HCAL."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from quasim.hcal.device import DeviceManager
from quasim.hcal.policy import PolicyValidator


@click.group()
@click.version_option()
def main() -> None:
    """HCAL - Hardware Control Abstraction Layer CLI."""
    pass


@main.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
def discover(output_json: bool) -> None:
    """Discover available hardware devices."""
    manager = DeviceManager()
    devices = manager.discover()
    
    if output_json:
        result = [
            {
                "id": d.id,
                "name": d.name,
                "type": d.type,
                "status": d.status,
                "properties": d.properties,
            }
            for d in devices
        ]
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Discovered {len(devices)} device(s):")
        for device in devices:
            click.echo(f"  - {device.name} ({device.id}): {device.status}")


@main.command()
@click.argument("policy_path", type=click.Path(exists=True, path_type=Path))
def validate_policy(policy_path: Path) -> None:
    """Validate a policy configuration file."""
    try:
        validator = PolicyValidator.from_file(policy_path)
        click.echo(f"✓ Policy validation passed")
        click.echo(f"  Environment: {validator.policy.environment}")
        click.echo(f"  Allowed backends: {', '.join(validator.policy.allowed_backends)}")
        click.echo(f"  Limits: {validator.policy.limits}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"✗ Policy validation failed: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
