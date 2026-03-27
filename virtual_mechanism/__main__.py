#!/usr/bin/env python
"""virtual mechanism - Main entry point
"""
import os
import signal
import sys
import time
import click
import yaml


@click.group()
@click.pass_context
def main(ctx, **kwargs):
    """Virtual mechanism - Device simulation with CAN bus communication
    """
    ctx.obj = {}


@main.command()
@click.option(
    '--mechanism', '-m',
    required=True,
    type=str,
    help='Mechanism name (e.g., SimpleClamp) or module path (e.g., pkg.module.MechClass)'
)
@click.option(
    '--dbc-file', '-d',
    default='',
    type=str,
    help='DBC file path'
)
@click.option(
    '--device', '-D',
    default='can0',
    type=str,
    help='CAN device name (default: can0)'
)
@click.option(
    '--config', '-c',
    default=None,
    type=str,
    help='YAML config file for mechanism-specific parameters'
)
@click.option(
    '--param', '-p',
    multiple=True,
    type=str,
    help='Mechanism parameter as key=value (repeatable)'
)
@click.pass_context
def run(ctx, mechanism, dbc_file, device, config, param):
    """Run virtual mechanism

    Examples:

        # Run built-in mechanism
        python -m virtual_mechanism run -m SimpleClamp -d ./clamp.dbc -D can0

        # Run with YAML config
        python -m virtual_mechanism run -m SimpleClamp -c ./config.yaml

        # Run with key=value parameters
        python -m virtual_mechanism run -m SimpleClamp -p max_speed=10.0 -p wheelbase=2.5

        # Run external mechanism
        python -m virtual_mechanism run -m my_mechanisms.MyMech -d ./my_mech.dbc
    """
    from virtual_mechanism.mechanisms import registry

    # Parse config file
    config_params = {}
    if config:
        if not os.path.exists(config):
            raise FileNotFoundError(f"Config file '{config}' does not exist.")
        with open(config, 'r') as f:
            config_params = yaml.safe_load(f) or {}

    # Parse -p parameters (override config file)
    cli_params = {}
    for p in param:
        if '=' not in p:
            raise click.BadParameter(f"Invalid parameter format: '{p}'. Use key=value")
        key, value = p.split('=', 1)
        # Try to parse as YAML for type inference
        try:
            cli_params[key] = yaml.safe_load(value)
        except yaml.YAMLError:
            cli_params[key] = value

    # Merge parameters (CLI overrides config)
    mech_params = {**config_params, **cli_params}

    # Add standard parameters if not provided
    if 'dbc_file' not in mech_params and dbc_file:
        mech_params['dbc_file'] = dbc_file
    if 'device' not in mech_params:
        mech_params['device'] = device

    # Validate DBC file if provided
    if 'dbc_file' in mech_params and mech_params['dbc_file']:
        dbc_path = mech_params['dbc_file']
        if not os.path.exists(dbc_path):
            raise FileNotFoundError(f"DBC file '{dbc_path}' does not exist.")

    # Load mechanism class
    try:
        mech_class = registry.load_mechanism(mechanism)
    except (ImportError, AttributeError, TypeError) as e:
        click.echo(f"Error loading mechanism '{mechanism}': {e}", err=True)
        sys.exit(1)

    # Instantiate mechanism
    try:
        mech = mech_class(**mech_params)
    except TypeError as e:
        click.echo(f"Error instantiating mechanism: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

    click.echo(f"Running mechanism: {mechanism}")
    click.echo(f"Device: {mech_params.get('device', 'can0')}")
    if 'dbc_file' in mech_params:
        click.echo(f"DBC file: {mech_params['dbc_file']}")

    # Start mechanism
    mech.run()

    def _signal_handler(sig, frame):
        """Signal handler for graceful shutdown
        """
        exit_signals = [signal.SIGINT, signal.SIGTERM]
        if sig in exit_signals:
            mech.shutdown()
            sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mech.shutdown()
        sys.exit(0)


@main.command()
@click.pass_context
def list(ctx):
    """List all available built-in mechanisms
    """
    from virtual_mechanism.mechanisms import registry

    mechanisms = registry.list_builtin_mechanisms()

    click.echo("Available built-in mechanisms:")
    click.echo()
    for name, path in mechanisms.items():
        click.echo(f"  {name:20s} {path}")
    click.echo()
    click.echo("To run external mechanisms, use full module path:")
    click.echo("  python -m virtual_mechanism run -m my_package.my_module.MyClass")


if __name__ == '__main__':
    main(obj={})
