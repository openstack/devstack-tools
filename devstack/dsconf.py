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

# Implementation of ini add / remove for devstack. We don't use the
# python ConfigFile parser because that ends up rewriting the entire
# file and doesn't ensure comments remain.

import re
import shutil
import tempfile


class IniFile(object):
    """Class for manipulating ini files in place."""

    def __init__(self, fname):
        self.fname = fname

    def add(self, section, name, value):
        """add a key / value to an ini file in a section.

        The new key value will be added at the beginning of the
        section, if no section is found a new section and key value
        will be added to the end of the file.
        """
        temp = tempfile.NamedTemporaryFile(mode='r')
        shutil.copyfile(self.fname, temp.name)
        found = False
        with open(temp.name) as reader:
            with open(self.fname, "w") as writer:
                for line in reader.readlines():
                    writer.write(line)
                    m = re.match("\[([^\[\]]+)\]", line)
                    if m and m.group(1) == section:
                        found = True
                        writer.write("%s = %s\n" % (name, value))
                if not found:
                    writer.write("[%s]\n" % section)
                    writer.write("%s = %s\n" % (name, value))

    def remove(self, section, name):
        """remove a key / value from an ini file in a section."""

        temp = tempfile.NamedTemporaryFile(mode='r')
        shutil.copyfile(self.fname, temp.name)
        current_section = ""
        with open(temp.name) as reader:
            with open(self.fname, "w") as writer:
                for line in reader.readlines():
                    m = re.match("\[([^\[\]]+)\]", line)
                    if m:
                        current_section = m.group(1)
                    if current_section == section:
                        if re.match("%s\s*\=" % name, line):
                            continue
                        else:
                            writer.write(line)
                    else:
                        writer.write(line)
