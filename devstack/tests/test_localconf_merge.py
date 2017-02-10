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
import os.path
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

LC1 = """
[[local|localrc]]
a=5
g=2
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1400
[[post-config|$GLANCE_CONF]]
[upgrade_levels]
compute = auto
"""

LC2 = """
[[local|localrc]]
# some other comment
enable_plugin ironic https://github.com/openstack/ironic
TEMPEST_PLUGINS+=" /opt/stack/new/ironic"
"""

RESULT1 = """
[[local|localrc]]
a=b
c=d
f=1
a=5
g=2
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu = 1400
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
[[post-config|$GLANCE_CONF]]
[upgrade_levels]
compute = auto
"""

RESULT2 = """
[[local|localrc]]
a=b
c=d
f=1
# some other comment
enable_plugin ironic https://github.com/openstack/ironic
TEMPEST_PLUGINS+=" /opt/stack/new/ironic"
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""


class TestLcMerge(testtools.TestCase):

    def setUp(self):
        super(TestLcMerge, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/local.conf"
        with open(self._path, "w") as f:
            f.write(BASIC)

    def test_merge_lc1(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        lc1 = os.path.join(dirname, "local1.conf")
        with open(lc1, "w+") as f:
            f.write(LC1)
        conf = dsconf.LocalConf(self._path)
        conf.merge_lc(lc1)

        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT1)

    def test_merge_lc2(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        lc2 = os.path.join(dirname, "local2.conf")
        with open(lc2, "w+") as f:
            f.write(LC2)
        conf = dsconf.LocalConf(self._path)
        conf.merge_lc(lc2)

        with open(self._path) as f:
            content = f.read()
            self.assertEqual(content, RESULT2)
