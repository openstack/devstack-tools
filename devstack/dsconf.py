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
                m = re.match(r"\[([^\[\]]+)\]", line)
                if m:
                    current_section = m.group(1)
                if current_section == section:
                    if re.match(r"%s\s*\=" % name, line):
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
                    m = re.match(r"\[([^\[\]]+)\]", line)
                    if m and m.group(1) == section:
                        found = True
                        writer.write("%s = %s\n" % (name, value))
            if not found:
                writer.write("[%s]\n" % section)
                writer.write("%s = %s\n" % (name, value))

    def _at_existing_key(self, section, name, func, match=r"%s\s*\="):
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
                    m = re.match(r"\[([^\[\]]+)\]", line)
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
            writer.write(re.sub(r"^#\s*", "", line))

        self._at_existing_key(section, name, _do_uncomment,
                              match=r"#\s*%s\s*\=")

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
            m = re.match(r"\[([^\[\]]+)\]", line)
            if m:
                current_section = m.group(1)
                continue
            else:
                m2 = re.match(r"(\w+)\s*\=\s*(.+)", line)
                if m2:
                    yield current_section, m2.group(1), m2.group(2)

    def groups(self):
        """Return a list of all groups in the local.conf"""
        groups = []
        with open(self.fname) as reader:
            for line in reader.readlines():
                m = re.match(r"\[\[([^\[\]]+)\|([^\[\]]+)\]\]", line)
                if m:
                    group = (m.group(1), m.group(2))
                    groups.append(group)
        return groups

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
                elif re.match(r"\[\[.*\|.*\]\]", line):
                    in_section = False
                    continue
                if in_section:
                    yield line

    def _has_local_section(self):
        for group in self.groups():
            if group == ("local", "localrc"):
                return True
        return False

    def extract(self, group, conf, target):
        ini_file = IniFile(target)
        for section, name, value in self._conf(group, conf):
            ini_file.set(section, name, value)

    def extract_localrc(self, target):
        with open(target, "a+") as f:
            for line in self._section("local", "localrc"):
                f.write(line)

    def _at_insert_point_local(self, name, func):
        """Run function when we are at the right insertion point in file.

        This lets us process an arbitrary file and insert content at
        the correct point. It has a few different state flags that we
        are looking for.

        Does this file have a local section at all? If not, we need to
        write one early in the file (this means we work with an empty
        file, as well as a file that has only post-config sections.

        Are we currently in a local section, if so, we need to write
        out content to the end, because items added to local always
        have to be added at the end.

        Did we write out the work that we expected? If so, just blast
        all lines to the end of the file.

        """
        temp = tempfile.NamedTemporaryFile(mode='r')
        shutil.copyfile(self.fname, temp.name)
        in_local = False
        has_local = self._has_local_section()
        done = False
        with open(self.fname, "w+") as writer:
            with open(temp.name) as reader:
                for line in reader.readlines():
                    if done:
                        writer.write(line)
                        continue

                    if re.match(re.escape("[[local|localrc]]"), line):
                        in_local = True
                    elif in_local and re.match(re.escape("[["), line):
                        func(writer, None)
                        done = True
                        in_local = False
                    elif not has_local and re.match(re.escape("[["), line):
                        writer.write("[[local|localrc]]\n")
                        func(writer, None)
                        done = True
                        in_local = False
                        has_local = True

                    # otherwise, just write what we found
                    writer.write(line)
            if not done:
                func(writer, None)

    def set_local(self, line):
        if not os.path.exists(self.fname):
            with open(self.fname, "w+") as writer:
                writer.write("[[local|localrc]]\n")
                writer.write("%s\n" % line.rstrip())
                return

        def _do_set(writer, no_line):
            writer.write("%s\n" % line.rstrip())
        self._at_insert_point_local(line, _do_set)

    def _at_insert_point(self, group, conf, section, name, func):
        temp = tempfile.NamedTemporaryFile(mode='r')
        shutil.copyfile(self.fname, temp.name)
        in_meta = False
        in_section = False
        done = False
        with open(self.fname, "w+") as writer:
            with open(temp.name) as reader:
                for line in reader.readlines():
                    if done:
                        writer.write(line)
                        continue

                    if re.match(re.escape("[[%s|%s]]" % (group, conf)), line):
                        in_meta = True
                        writer.write(line)
                    elif re.match(r"\[\[.*\|.*\]\]", line):
                        # if we're not done yet, we
                        if in_meta:
                            if not in_section:
                                # if we've not found the section yet,
                                # write out section as well.
                                writer.write("[%s]\n" % section)
                            func(writer, None)
                            done = True
                        writer.write(line)
                        in_meta = False
                        in_section = False
                    elif re.match(re.escape("[%s]" % section), line):
                        # we found a relevant section
                        writer.write(line)
                        in_section = True
                    elif re.match(r"\[[^\[\]]+\]", line):
                        if in_meta and in_section:
                            # We've ended our section, in our meta,
                            # never found the key. Time to add it.
                            func(writer, None)
                            done = True
                        in_section = False
                        writer.write(line)
                    elif (in_meta and in_section and
                          re.match(r"\s*%s\s*\=" % re.escape(name), line)):
                        # we found our match point
                        func(writer, line)
                        done = True
                    else:
                        # write out whatever we find
                        writer.write(line)
            if not done:
                if not in_meta:
                    writer.write("[[%s|%s]]\n" % (group, conf))
                    in_section = False
                if not in_section:
                    writer.write("[%s]\n" % (section))
                func(writer, None)

    def set(self, group, conf, section, name, value):
        if not os.path.exists(self.fname):
            with open(self.fname, "w+") as writer:
                writer.write("[[%s|%s]]\n" % (group, conf))
                writer.write("[%s]\n" % section)
                writer.write("%s = %s\n" % (name, value))
                return

        def _do_set(writer, line):
            writer.write("%s = %s\n" % (name, value))
        self._at_insert_point(group, conf, section, name, _do_set)

    def merge_lc(self, lcfile):
        lc = LocalConf(lcfile)
        groups = lc.groups()
        for group, conf in groups:
            if group == "local":
                for line in lc._section(group, conf):
                    self.set_local(line)
            else:
                for section, name, value in lc._conf(group, conf):
                    self.set(group, conf, section, name, value)
