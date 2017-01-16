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

import fixtures
import testtools

from devstack import dsconf


BASIC = """[default]
a = b
c = d
[second]
e = f
g = h
[new]
s = t
"""

RESULT1 = """[default]
a = 2
c = d
[second]
e = f
g = h
[new]
s = t
"""

RESULT2 = """[default]
a = b
c = d
[second]
e = f
g = 2
[new]
s = t
"""

RESULT3 = """[default]
a = b
c = d
[second]
e = f
g = h
[new]
s = 2
"""

RESULT4 = """[default]
s = 2
a = b
c = d
[second]
e = f
g = h
[new]
s = t
"""


class TestIniSet(testtools.TestCase):

    def setUp(self):
        super(TestIniSet, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/test.ini"
        with open(self._path, "w") as f:
            f.write(BASIC)

    def test_set_ini_default(self):
        conf = dsconf.IniFile(self._path)
        conf.set("default", "a", "2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT1)

    def test_set_ini_second(self):
        conf = dsconf.IniFile(self._path)
        conf.set("second", "g", "2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT2)

    def test_set_ini_new(self):
        conf = dsconf.IniFile(self._path)
        conf.set("new", "s", "2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT3)

    def test_set_ini_none(self):
        conf = dsconf.IniFile(self._path)
        conf.set("default", "s", "2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT4)


class TestIniCreate(testtools.TestCase):

    def setUp(self):
        super(TestIniCreate, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/test.ini"

    def test_add_items(self):
        conf = dsconf.IniFile(self._path)
        conf.set("default", "c", "d")
        conf.set("default", "a", "b")
        conf.set("second", "g", "h")
        conf.set("second", "e", "f")
        conf.set("new", "s", "t")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(BASIC, content)
