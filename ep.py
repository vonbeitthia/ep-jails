#!/usr/bin/env python3

#-
# Copyright (c) 2019 Tom Marcoen
# All rights reserved.
#-
# This script assumes the bridges (IF_BRIDGE(4)) have been created
# in advance, e.g. in /etc/rc.conf, and will only create a pair of
# virtual back-to-back connected Ethernet interfaces for use with
# jails.
#
# Excerpt /etc/rc.conf:
#
#    cloned_interfaces="bridge0 bridge1"
#    ifconfig_bridge0_name="b0_wan"
#    ifconfig_bridge1_name="b1_dmz"
#
# Excerpt /etc/jail.conf:
#
#    XXX {
#       vnet;
#       vnet.interface = e0a_wan_XXX, e0a_dmz_XXX;
#       exec.prestart = "ep.py create XXX wan dmz";
#       exec.poststop = "ep.py destroy XXX wan dmz";
#-

import argparse
from pprint import pprint
from re import sub
from subprocess import Popen, PIPE, STDOUT
from sys import exit

IF_NAMESIZE = 16 # /sys/net/if.h
debug_level = 0


# usage: ep.py create [-h] name bridge [bridge ...]
#
# For each bridge listed, create an epair and assign one end to the jail
# and the other to the bridge.
def create(args):
    jail = args['name']
    if (debug_level>=2): print("[DEBUG] Jail name: {}".format(jail))
    # Loop through the list of bridges and create an epair for each.
    for i, bridge in enumerate(args['bridge']):
        if (debug_level>=2): print("[DEBUG] Bridge: {}".format(bridge))
        # Create a new epair
        output = Popen('ifconfig epair create'.split(),
                stdout=PIPE,
                stderr=STDOUT)
        stdout,stderr = output.communicate()
        epair = stdout.decode('UTF-8').strip()
        if (debug_level>=2): print("[DEBUG] epair: {}".format(epair))
        # Rename the epair and bring the interfaces up
        new_a = 'e' + str(i) + 'a_' + bridge + '_' + jail
        new_b = 'e' + str(i) + 'b_' + bridge + '_' + jail
        if (len(new_a)>=IF_NAMESIZE):
            print("[ERROR] Interface name too long.")
            exit(1)
        if (debug_level>=2): print("[DEBUG] new_a: {}".format(new_a))
        if (debug_level>=2): print("[DEBUG] new_b: {}".format(new_b))
        if (debug_level>=1): print("[INFO] Creating {}...".format(new_a))
        output = Popen('ifconfig {} name {} up'.format(epair,new_a).split(),
                stdout=PIPE,
                stderr=STDOUT)
        stdout,stderr = output.communicate()
        if (debug_level>=2):
            print("[DEBUG] out: {}".format(stdout))
            print("[DEBUG] err: {}".format(stderr))
        if (debug_level>=1): print("[INFO] Creating {}...".format(new_b))
        output = Popen('ifconfig {} name {} up'.format(sub('a$','b', epair),new_b).split(),
                stdout=PIPE,
                stderr=STDOUT)
        # Attach one end to the bridge
        if (args['aside']):
            output = Popen('ifconfig {} addm {}'.format(bridge, new_a).split(),
                stdout=PIPE,
                stderr=STDOUT)
        else:
            output = Popen('ifconfig {} addm {}'.format(bridge, new_b).split(),
                stdout=PIPE,
                stderr=STDOUT)
    return


def destroy(args):
    jail = args['name']
    if (debug_level>=2): print("[DEBUG] Jail: {}".format(jail))
    for i, bridge in enumerate(args['bridge']):
        if (debug_level>=2): print("[DEBUG] Bridge: {}".format(bridge))
        intf = 'e' + str(i) + 'a_' + bridge + '_' + jail
        if (debug_level>=1): print('[INFO] Destroying {}...'.format(intf))
        output = Popen('ifconfig {} destroy'.format(intf).split(),
                stdout=PIPE,
                stderr=STDOUT)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create and destroy epair interfaces for jails.')
    # Option: verbosity in debug level
    parser.add_argument('-v', '--verbose',
            action='count', default=0,
            help='Increase the verbosity level by adding this argument multiple times.')
    # Option: use the 'A' side of the epair instead of the default 'B' pair
    parser.add_argument('-a', '--aside',
            action='store_true',
            help="Use the 'A' side of the epair instead of the default 'B' pair.")

    # We have two commands: create new interfaces or destroy existing ones.
    subparsers = parser.add_subparsers(title='Commands',dest='cmd')
    # Command: create
    parser_create = subparsers.add_parser(
            'create',
            help='Create epair interfaces for the given jail.')
    parser_create.add_argument('name', help='The name of the jail')
    parser_create.add_argument('bridge', nargs='+')
    # Command: destroy
    parser_destroy = subparsers.add_parser(
            'destroy', 
            help='Destroy the epair interfaces for the given jail.')
    parser_destroy.add_argument('name', help='The name of the jail')
    parser_destroy.add_argument('bridge', nargs='+')

    # Parse the argument and call the function create() or destroy()
    args = parser.parse_args()
    debug_level = vars(args)['verbose']
    # There must be a better way to write this...
    if (vars(args)['cmd'] == 'create'):
        create(vars(args))
    elif (vars(args)['cmd'] == 'destroy'):
        destroy(vars(args))
