import argparse
import sys

USAGE = """cardice command [options...]"""


def make_parser():
    """Parse commandline arguments using a git-like subcommands scheme"""

    common_parser = argparse.ArgumentParser(
        add_help=False,
    )
    common_parser.add_argument(
        "--cardice-folder",
        default="~/.cardice",
        help="Folder to store the cardice configuration and cluster info."
    )
    common_parser.add_argument(
        "--log-level",
        default="INFO",
        help="Minimum log level for the file log (under NXDRIVE_HOME/logs)."
    )
    common_parser.add_argument(
        "--cluster",
        default=None,
        help="Perform the command on a specific cluster. "
             "Otherwise the default cluster is the last selected cluster."
    )
    parser = argparse.ArgumentParser(
        parents=[common_parser],
        usage=USAGE,
    )

    subparsers = parser.add_subparsers(
        title='valid commands',
    )

    # init a cluster config
    init_parser = subparsers.add_parser(
        'init', help='Create a new cluster configuration.',
        parents=[common_parser],
        usage="cardice init name",
    )
    init_parser.set_defaults(command='init')
    init_parser.add_argument(
        "name", help="Name of a new cluster configuration.")

    start_parser = subparsers.add_parser(
        'start', help="Start the selected cluster configuration.",
        parents=[common_parser],
    )
    start_parser.set_defaults(command='start')

    stop_parser = subparsers.add_parser(
        'stop', help="Stop the selected cluster configuration.",
        parents=[common_parser],
    )
    stop_parser.set_defaults(command='stop')

    terminate_parser = subparsers.add_parser(
        'terminate', help="Stop the selected cluster configuration and free"
                          " all related cloud resources. WARNING: all unsaved"
                          " data will be lost.",
        parents=[common_parser],
    )
    terminate_parser.set_defaults(command='terminate')
    return parser


class CommandHandler(object):
    """Dispatch the commandline instructions to the right component."""

    def __init__(self, options):
        self.options = options
        # TODO: check or initialize the cardice config folder
        # TODO: configure the logger

    def run(self):
        """Execute the specified command parameterized by CLI options"""
        getattr(self, 'run_' + self.options.command)

    def interrupt(self, cmd, options):
        """Perform clean up operations on user interuptions (if any)"""
        handler = getattr(self, 'interrupt_' + cmd, None)
        if handler is not None:
            return handler(options)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = make_parser()
    options = parser.parse_args(args)
    
    executor = CommandHandler(options)
    try:
        executor.run()
    except KeyboardInterrupt:
        executor.interupt()
