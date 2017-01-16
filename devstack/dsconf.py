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

import os.path
import re
import shutil
import tempfile


class IniFile(object):
    """Class for manipulating ini files in place."""

    def __init__(self, fname):
        self.fname = fname

    def has(self, section, name):
        """Returns True if section has a key that is name"""

        current_section = ""
        if not os.path.exists(self.fname):
            return False

        with open(self.fname, "r+") as reader:
            for line in reader.readlines():
                m = re.match("\[([^\[\]]+)\]", line)
                if m:
                    current_section = m.group(1)
                if current_section == section:
                    if re.match("%s\s*\=" % name, line):
                        return True
        return False

    def add(self, section, name, value):
        """add a key / value to an ini file in a section.

        The new key value will be added at the beginning of the
        section, if no section is found a new section and key value
        will be added to the end of the file.
        """
        temp = tempfile.NamedTemporaryFile(mode='r')
        if os.path.exists(self.fname):
            shutil.copyfile(self.fname, temp.name)
        else:
            with open(temp.name, "w+"):
                pass

        found = False
        with open(self.fname, "w+") as writer:
            with open(temp.name) as reader:
                for line in reader.readlines():
                    writer.write(line)
                    m = re.match("\[([^\[\]]+)\]", line)
                    if m and m.group(1) == section:
                        found = True
                        writer.write("%s = %s\n" % (name, value))
            if not found:
                writer.write("[%s]\n" % section)
                writer.write("%s = %s\n" % (name, value))

    def _at_existing_key(self, section, name, func, match="%s\s*\="):
        """Run a function at a found key.

        NOTE(sdague): if the file isn't found, we end up
        exploding. This seems like the right behavior in nearly all
        circumstances.

        """
        temp = tempfile.NamedTemporaryFile(mode='r')
        shutil.copyfile(self.fname, temp.name)
        current_section = ""
        with open(temp.name) as reader:
            with open(self.fname, "w+") as writer:
                for line in reader.readlines():
                    m = re.match("\[([^\[\]]+)\]", line)
                    if m:
                        current_section = m.group(1)
                    if current_section == section:
                        if re.match(match % name, line):
                            # run function with writer and found line
                            func(writer, line)
                        else:
                            writer.write(line)
                    else:
                        writer.write(line)

    def remove(self, section, name):
        """remove a key / value from an ini file in a section."""
        def _do_remove(writer, line):
            pass

        self._at_existing_key(section, name, _do_remove)

    def comment(self, section, name):
        def _do_comment(writer, line):
            writer.write("# %s" % line)

        self._at_existing_key(section, name, _do_comment)

    def uncomment(self, section, name):
        def _do_uncomment(writer, line):
            writer.write(re.sub("^#\s*", "", line))

        self._at_existing_key(section, name, _do_uncomment,
                              match="#\s*%s\s*\=")

    def set(self, section, name, value):
        def _do_set(writer, line):
            writer.write("%s = %s\n" % (name, value))
        if self.has(section, name):
            self._at_existing_key(section, name, _do_set)
        else:
            self.add(section, name, value)


class LocalConf(object):
    """Class for manipulating local.conf files in place."""

    def __init__(self, fname):
        self.fname = fname

    def _conf(self, group, conf):
        current_section = ""
        for line in self._section(group, conf):
            m = re.match("\[([^\[\]]+)\]", line)
            if m:
                current_section = m.group(1)
                continue
            else:
                m2 = re.match(r"(\w+)\s*\=\s*(.+)", line)
                if m2:
                    yield current_section, m2.group(1), m2.group(2)

    def _section(self, group, conf):
        """Yield all the lines out of a meta section."""
        in_section = False
        with open(self.fname) as reader:
            for line in reader.readlines():
                if re.match(r"\[\[%s\|%s\]\]" % (
                        re.escape(group),
                        re.escape(conf)),
                        line):
                    in_section = True
                    continue
                # any other meta section means we aren't in the
                # section we want to be.
                elif re.match("\[\[.*\|.*\]\]", line):
                    in_section = False
                    continue
                if in_section:
                    yield line

    def extract(self, group, conf, target):
        ini_file = IniFile(target)
        for section, name, value in self._conf(group, conf):
            ini_file.set(section, name, value)

    def extract_localrc(self, target):
        with open(target, "a+") as f:
            for line in self._section("local", "localrc"):
                f.write(line)
