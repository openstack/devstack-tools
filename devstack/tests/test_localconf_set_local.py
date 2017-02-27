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


BASIC = """
[[local|localrc]]
a=b
c=d
f=1
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

BASIC_NO_LOCAL = """
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

RESULT1 = """
[[local|localrc]]
a=b
c=d
f=1
g=2
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

RESULT2 = """
[[local|localrc]]
a=b
c=d
f=1
a=2
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

RESULT3 = """
[[local|localrc]]
a=b
c=d
f=1
enable_plugin foo http://foo branch
enable_plugin bar http://foo branch
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

RESULT_NO_LOCAL = """
[[local|localrc]]
a=b
c=d
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""


class TestLcSet(testtools.TestCase):

    def setUp(self):
        super(TestLcSet, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/local.conf"
        with open(self._path, "w") as f:
            f.write(BASIC)

    def test_set_new(self):
        conf = dsconf.LocalConf(self._path)
        conf.set_local("g=2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT1)

    def test_set_existing(self):
        conf = dsconf.LocalConf(self._path)
        conf.set_local("a=2")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT2)

    def test_set_raw(self):
        conf = dsconf.LocalConf(self._path)
        conf.set_local("enable_plugin foo http://foo branch")
        conf.set_local("enable_plugin bar http://foo branch")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT3)

    def test_set_raw_multiline(self):
        conf = dsconf.LocalConf(self._path)
        conf.set_local("enable_plugin foo http://foo branch"
                       "\nenable_plugin bar http://foo branch")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT3)


class TestNoLocal(testtools.TestCase):

    def setUp(self):
        super(TestNoLocal, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/local.conf"
        with open(self._path, "w") as f:
            f.write(BASIC_NO_LOCAL)

    def test_set_new(self):
        conf = dsconf.LocalConf(self._path)
        conf.set_local("a=b")
        conf.set_local("c=d")
        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT_NO_LOCAL)
