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


def parse_args(argv):
    parser = argparse.ArgumentParser(prog='dsconf')
    subparsers = parser.add_subparsers(title='commands',
                                       help='sub-command help')

    parser_iniset = subparsers.add_parser('iniset', help='iniset help')
    parser_iniset.set_defaults(func=iniset)
    parser_iniset.add_argument('inifile', help='name of file')
    parser_iniset.add_argument('section', help='name of section')
    parser_iniset.add_argument('name', help='name')
    parser_iniset.add_argument('value', help='value')

    parser_inicomment = subparsers.add_parser('inicomment', help='inicomment help')
    parser_inicomment.set_defaults(func=inicomment)
    parser_inicomment.add_argument('inifile', help='name of file')
    parser_inicomment.add_argument('section', help='name of section')
    parser_inicomment.add_argument('name', help='name')

    parser_iniuncomment = subparsers.add_parser('iniuncomment', help='iniuncomment help')
    parser_iniuncomment.set_defaults(func=iniuncomment)
    parser_iniuncomment.add_argument('inifile', help='name of file')
    parser_iniuncomment.add_argument('section', help='name of section')
    parser_iniuncomment.add_argument('name', help='name')

    parser_inirm = subparsers.add_parser('inirm', help='inirm help')
    parser_inirm.set_defaults(func=inirm)
    parser_inirm.add_argument('inifile', help='name of file')
    parser_inirm.add_argument('section', help='name of section')
    parser_inirm.add_argument('name', help='name')

    return parser.parse_args()


def main(argv=None):
    args = parse_args(argv or sys.argv)
    if hasattr(args, 'inifile'):
        f = devstack.dsconf.IniFile(args.inifile)
    args.func(f, args)
    return
