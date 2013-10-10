import argparse
import sys

from cardice.config import Configurator
from cardice.provision import Provisioner


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

    select_parser = subparsers.add_parser(
        'select', help="Mark the requested cluster as the default cluster.",
        parents=[common_parser],
    )
    select_parser.set_defaults(command='select')
    select_parser.add_argument(
        "name", help="Name of the cluster configuration to select"
                     " as default cluster.")

    start_parser = subparsers.add_parser(
        'start', help="Start the selected cluster configuration.",
        parents=[common_parser],
    )
    start_parser.set_defaults(command='start')
    start_parser.add_argument(
        "profile",
        help="Name of the profile to use to provision new nodes.")
    start_parser.add_argument(
        "--n-nodes", default=1, help="Number of nodes to start.")
    start_parser.add_argument(
        "--name-prefix", default="node",
        help="Prefix for the new node names.")

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
        self.config = Configurator(options)

    def run(self):
        """Execute the specified command parameterized by CLI options"""
        getattr(self, 'run_' + self.options.command)()

    def interrupt(self):
        """Perform clean up operations on user interuptions (if any)"""
        handler = getattr(self, 'interrupt_' + self.options.command, None)
        if handler is not None:
            return handler()

    def run_init(self):
        self.config.init_cluster(self.options.name)

    def run_select(self):
        self.config.set_default_cluster(self.options.name)

    def run_start(self):
        provisioner = Provisioner(self.config)
        provisioner.start(self.options.profile,
                          n_nodes=self.options.n_nodes,
                          name_prefix=self.options.name_prefix)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = make_parser()
    options = parser.parse_args(args)
    
    handler = CommandHandler(options)
    try:
        handler.run()
    except KeyboardInterrupt:
        handler.interupt()
    except Exception as e:
        if options.log_level.upper() == 'DEBUG':
            raise
        else:
            handler.config.log.error(str(e))
            sys.exit(1)
