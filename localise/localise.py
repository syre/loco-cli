#!/usr/bin/env python

import argparse
from colorama import init, Fore, Back, Style
from commands import *
import signal
import sys

class ConfigException(Exception):
    """Raise when config file is invalid"""

def signal_handler(signal, frame):
    print("\nInterrupted!")
    sys.exit(0)

def get_configuration(args):
    """
    Parse configuration file

    Throw an exception when file does not exists or has wrong format.
    :param args:
    :return:
    """
    from os.path import expanduser
    home = expanduser("~")
    config_file = home + '/.localise/config.yml'
    if hasattr(args, 'config_file'):
        config_file = args.config_file

    if not os.path.isfile(config_file):
        print(Fore.RED + 'No configuration file found! Run the following command to create one:' + Style.RESET_ALL)
        print('')
        print('    localize config')
        print('')
        print('You can also create the file manually in your $HOME directory: $HOME/.localise/config.yml')
        print('')
        sys.exit()

    with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    return cfg


def command(args):
    if not args.command == 'config':
        try:
            configuration = get_configuration(args)
        except ConfigException as e:
            print(e.message)
            return

    try:
        if args.command == 'list':
            print("Available projects:")
            for section in configuration:
                print(section)
        elif args.command == 'push':
            check_config_section(configuration, args.project)
            push(configuration[args.project], args)
        elif args.command == 'pull':
            check_config_section(configuration, args.project)
            pull(configuration[args.project], args)
        elif args.command == 'config':
            config(args)
        else:
            sys.exit(Fore.RED + "Not a valid command \"%s\"! Did you mean config, push, or pull?" % (
            args.command) + Style.RESET_ALL)
    except ConfigException as e:
        print(e.message)
        return


def parse_args():
    p = argparse.ArgumentParser(description='Localise')
    p.add_argument('command', help='Specify command: push, pull, config, list')
    p.add_argument('project', nargs='?', help='Specify project name')

    p.add_argument("-c", "--config", dest="config_file", help="Specify config file", metavar="FILE")
    p.add_argument('--verbose', '-v', action='count')

    args = p.parse_args()

    return args


def main():
    if sys.version_info >= (3, 0):
        sys.exit('Sorry, Python >= 3.0 is not supported')

    init(autoreset=True)
    args = parse_args()
    command(args)

def check_config_section(cfg, section):
    if not section in cfg:
        raise ConfigException('Unknown project identificator "%s"' % (section))
    if not 'api' in cfg[section] or not 'token' in cfg[section]['api'] or not cfg[section]['api']['token']:
        raise ConfigException('Missing token value in config file')
    if not 'translations' in cfg[section]:
        raise ConfigException('No translation files defined in config file')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
