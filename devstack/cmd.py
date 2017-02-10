# Copyright 2017 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import sys

import devstack.dsconf


def iniset(inifile, args):
    inifile.set(args.section, args.name, args.value)


def inirm(inifile, args):
    inifile.remove(args.section, args.name)


def inicomment(inifile, args):
    inifile.comment(args.section, args.name)


def iniuncomment(inifile, args):
    inifile.uncomment(args.section, args.name)


def extract_local(local_conf, args):
    local_conf.extract_localrc(args.local_rc)


def extract_config(local_conf, args):
    local_conf.extract(args.group, args.conf, args.local_rc)


def setlc(local_conf, args):
    local_conf.set_local("%s=%s" % (args.name, args.value))


def setlc_raw(local_conf, args):
    local_conf.set_local(" ".join(args.items))


def setlc_conf(local_conf, args):
    local_conf.set(args.group, args.conf, args.section, args.name, args.value)


def merge(local_conf, args):
    for source in args.sources:
        local_conf.merge_lc(source)


def parse_args(argv):
    parser = argparse.ArgumentParser(prog='dsconf')
    subparsers = parser.add_subparsers(title='commands',
                                       help='sub-command help')

    parser_iniset = subparsers.add_parser('iniset',
                                          help='set item in ini file')
    parser_iniset.set_defaults(func=iniset)
    parser_iniset.add_argument('inifile', help='name of file')
    parser_iniset.add_argument('section', help='name of section')
    parser_iniset.add_argument('name', help='name')
    parser_iniset.add_argument('value', help='value')

    parser_inicomment = subparsers.add_parser(
        'inicomment',
        help='comment item in ini file')
    parser_inicomment.set_defaults(func=inicomment)
    parser_inicomment.add_argument('inifile', help='name of file')
    parser_inicomment.add_argument('section', help='name of section')
    parser_inicomment.add_argument('name', help='name')

    parser_iniuncomment = subparsers.add_parser(
        'iniuncomment',
        help='uncomment item in ini file')
    parser_iniuncomment.set_defaults(func=iniuncomment)
    parser_iniuncomment.add_argument('inifile', help='name of file')
    parser_iniuncomment.add_argument('section', help='name of section')
    parser_iniuncomment.add_argument('name', help='name')

    parser_inirm = subparsers.add_parser(
        'inirm',
        help='delete item from ini file')
    parser_inirm.set_defaults(func=inirm)
    parser_inirm.add_argument('inifile', help='name of file')
    parser_inirm.add_argument('section', help='name of section')
    parser_inirm.add_argument('name', help='name')

    parser_extract_local = subparsers.add_parser(
        'extract-localrc',
        help='extract localrc from local.conf')
    parser_extract_local.set_defaults(func=extract_local)
    parser_extract_local.add_argument('local_conf')
    parser_extract_local.add_argument('local_rc')

    parser_extract = subparsers.add_parser(
        'extract',
        help='extract and merge config from local.conf')
    parser_extract.set_defaults(func=extract_config)
    parser_extract.add_argument('local_conf')
    parser_extract.add_argument('group')
    parser_extract.add_argument('conf')
    parser_extract.add_argument('local_rc')

    parser_setlc = subparsers.add_parser(
        'setlc', help='set variable in localrc of local.conf')
    parser_setlc.set_defaults(func=setlc)
    parser_setlc.add_argument('local_conf')
    parser_setlc.add_argument('name')
    parser_setlc.add_argument('value')

    parser_setlc_raw = subparsers.add_parser(
        'setlc_raw', help='set raw line at the end of localrc in local.conf')
    parser_setlc_raw.set_defaults(func=setlc_raw)
    parser_setlc_raw.add_argument('local_conf')
    parser_setlc_raw.add_argument('items', nargs="+")

    parser_setlc_conf = subparsers.add_parser(
        'setlc_conf', help='set variable in ini section of local.conf')
    parser_setlc_conf.set_defaults(func=setlc_conf)
    parser_setlc_conf.add_argument('local_conf')
    parser_setlc_conf.add_argument('group')
    parser_setlc_conf.add_argument('conf')
    parser_setlc_conf.add_argument('section')
    parser_setlc_conf.add_argument('name')
    parser_setlc_conf.add_argument('value')

    parser_merge = subparsers.add_parser(
        'merge_lc', help='merge local.conf files')
    parser_merge.set_defaults(func=merge)
    parser_merge.add_argument('local_conf')
    parser_merge.add_argument('sources', nargs='+')

    return parser.parse_args(), parser


def main(argv=None):
    args, parser = parse_args(argv or sys.argv)
    if hasattr(args, 'inifile'):
        f = devstack.dsconf.IniFile(args.inifile)
    elif hasattr(args, 'local_conf'):
        f = devstack.dsconf.LocalConf(args.local_conf)

    if hasattr(args, 'func'):
        args.func(f, args)
    else:
        parser.print_help()
        return 1
    return
