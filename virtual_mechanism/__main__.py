#!/usr/bin/env python
"""apollo keyboard controller
"""
import os
import signal
import sys
import time
import click
from virtual_mechanism.mechanisms import simple_clamp


@click.group()
@click.pass_context
def main(ctx, **kwargs):
    """virtual mechanism
    """


@main.command()
@click.option('--dbc_file', default='', type=str, help='dbc file')
@click.option('--device', default='can0', type=str, help='can device')
@click.pass_context
def run(ctx, **kwargs):
    """run virtual mechanism
    """
    dbc_file = kwargs.get('dbc_file', './mechanism.dbc')
    device = kwargs.get('device', 'can0')

    if dbc_file and not os.path.exists(dbc_file):
        raise FileNotFoundError(f"DBC file '{dbc_file}' does not exist.")

    # TODO(All): select mechanism type by command line arguments
    # TODO(All): support multiple mechanisms and plugins
    mech = simple_clamp.SimpleClamp(dbc_file=dbc_file, device=device)
    mech.run()

    def _signal_handler(sig, frame):
        """signal_handler
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


if __name__ == '__main__':
    main(obj={})
