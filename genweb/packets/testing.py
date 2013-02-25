from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import genweb.packets


GENWEB_PACKETS = PloneWithPackageLayer(
    zcml_package=genweb.packets,
    zcml_filename='testing.zcml',
    gs_profile_id='genweb.packets:testing',
    name="GENWEB_PACKETS")

GENWEB_PACKETS_INTEGRATION = IntegrationTesting(
    bases=(GENWEB_PACKETS, ),
    name="GENWEB_PACKETS_INTEGRATION")

GENWEB_PACKETS_FUNCTIONAL = FunctionalTesting(
    bases=(GENWEB_PACKETS, ),
    name="GENWEB_PACKETS_FUNCTIONAL")
