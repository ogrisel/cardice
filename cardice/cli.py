import argparse
import sys


def parse_arguments(args):
    # TODO
    pass

class CommandHandler(object):

    def __init__(self, common_opts):
        self.common_opts = common_opts


    def handle(self, cmd, options):
        """Execute the specified command parameterized by CLI options"""
        getattr(self, cmd)(options)

    def interrupt(self, cmd, options):
        """Perform clean up operations on user interuptions (if any)"""
        handler = getattr(self, '' + cmd, None)
        if handler is not None:
            return handler(options)


def main(args=None):
    if args is None:
        args = sys.argv
    common_opts, cmd, cmd_opts = parse_arguments(args)
    
    executor = CommandHandler(common_opts)
    try:
        executor.handle(cmd, cmd_opts)
    except KeyboardInterrupt:
        executor.interupt(cmd, cmd_opts)
