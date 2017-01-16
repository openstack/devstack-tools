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
a = b
c = d
f = 1
[[post-config|$NEUTRON_CONF]]
[DEFAULT]
global_physnet_mtu=1450
[[post-config|$NOVA_CONF]]
[upgrade_levels]
compute = auto
"""

LOCALRC = """a = 1
c = b
"""

LOCALRC_RES = """a = 1
c = b
a = b
c = d
f = 1
"""

NOVA = """[upgrade_levels]
compute = auto
"""

NEUTRON = """[DEFAULT]
global_physnet_mtu = 1450
"""

NEUTRON_BASE = """[DEFAULT]
api_workers = 2
"""

NEUTRON_BASE_RES = """[DEFAULT]
global_physnet_mtu = 1450
api_workers = 2
"""

NEUTRON_BASE2 = """[DEFAULT]
api_workers = 2
global_physnet_mtu = 1400
"""

NEUTRON_BASE2_RES = """[DEFAULT]
api_workers = 2
global_physnet_mtu = 1450
"""


class TestLcExtract(testtools.TestCase):

    def setUp(self):
        super(TestLcExtract, self).setUp()
        self._path = self.useFixture(fixtures.TempDir()).path
        self._path += "/local.conf"
        with open(self._path, "w") as f:
            f.write(BASIC)

    def test_extract_neutron(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        neutron = os.path.join(dirname, "neutron.conf")
        nova = os.path.join(dirname, "nova.conf")
        conf = dsconf.LocalConf(self._path)
        conf.extract("post-config", "$NEUTRON_CONF", neutron)
        conf.extract("post-config", "$NOVA_CONF", nova)

        with open(neutron) as f:
            content = f.read()
            self.assertEqual(content, NEUTRON)

        with open(nova) as f:
            content = f.read()
            self.assertEqual(content, NOVA)

    def test_extract_neutron_merge_add(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        neutron = os.path.join(dirname, "neutron.conf")
        with open(neutron, "w+") as f:
            f.write(NEUTRON_BASE)

        conf = dsconf.LocalConf(self._path)
        conf.extract("post-config", "$NEUTRON_CONF", neutron)

        with open(neutron) as f:
            content = f.read()
            self.assertEqual(content, NEUTRON_BASE_RES)

    def test_extract_neutron_merge_set(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        neutron = os.path.join(dirname, "neutron.conf")
        with open(neutron, "w+") as f:
            f.write(NEUTRON_BASE2)

        conf = dsconf.LocalConf(self._path)
        conf.extract("post-config", "$NEUTRON_CONF", neutron)

        with open(neutron) as f:
            content = f.read()
            self.assertEqual(content, NEUTRON_BASE2_RES)

    def test_extract_localrc(self):
        dirname = self.useFixture(fixtures.TempDir()).path
        localrc = os.path.join(dirname, "localrc")
        with open(localrc, "w+") as f:
            f.write(LOCALRC)

        conf = dsconf.LocalConf(self._path)
        conf.extract_localrc(localrc)

        with open(localrc) as f:
            content = f.read()
            self.assertEqual(content, LOCALRC_RES)
