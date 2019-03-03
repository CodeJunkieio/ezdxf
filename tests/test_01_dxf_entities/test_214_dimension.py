# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-15
import pytest

from ezdxf.entities.dimension import Dimension
from ezdxf.lldxf.const import DXF12, DXF2000
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text

TEST_CLASS = Dimension
TEST_TYPE = 'DIMENSION'

ENTITY_R12 = """0
DIMENSION
5
0
8
0
2
*D0
3
Standard
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
12
0.0
22
0.0
32
0.0
70
0
1

13
0.0
23
0.0
33
0.0
14
0.0
24
0.0
34
0.0
15
0.0
25
0.0
35
0.0
16
0.0
26
0.0
36
0.0
40
1.0
50
0.0
"""

ENTITY_R2000 = """  0
DIMENSION
5
0
330
0
100
AcDbEntity
8
0
100
AcDbDimension
2
*D0
3
Standard
10
0.0
20
0.0
30
0.0
11
0.0
21
0.0
31
0.0
70
32
71
5
42
0.0
100
AcDbAlignedDimension
 13
0.0
 23
0.0
 33
0.0
 14
0.0
 24
0.0
 34
0.0
50
0
100
AcDbRotatedDimension
"""


@pytest.fixture(params=[ENTITY_R12, ENTITY_R2000])
def entity(request):
    return TEST_CLASS.from_text(request.param)


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert TEST_TYPE in ENTITY_CLASSES


def test_default_init():
    entity = TEST_CLASS()
    assert entity.dxftype() == TEST_TYPE


def test_default_new():
    entity = TEST_CLASS.new(handle='ABBA', owner='0', dxfattribs={
        'color': '7',
        'defpoint': (1, 2, 3),
    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.linetype == 'BYLAYER'
    assert entity.dxf.defpoint == (1, 2, 3)
    assert entity.dxf.defpoint.x == 1, 'is not Vector compatible'
    assert entity.dxf.defpoint.y == 2, 'is not Vector compatible'
    assert entity.dxf.defpoint.z == 3, 'is not Vector compatible'
    # can set DXF R2007 value
    entity.dxf.shadow_mode = 1
    assert entity.dxf.shadow_mode == 1


def test_load_from_text(entity):
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.defpoint == (0, 0, 0)


@pytest.mark.parametrize("txt,ver", [(ENTITY_R2000, DXF2000), (ENTITY_R12, DXF12)])
def test_write_dxf(txt, ver):
    expected = basic_tags_from_text(txt)
    dimension = TEST_CLASS.from_text(txt)
    collector = TagCollector(dxfversion=ver, optional=True)
    dimension.export_dxf(collector)
    assert collector.tags == expected

    collector2 = TagCollector(dxfversion=ver, optional=False)
    dimension.export_dxf(collector2)
    assert collector.has_all_tags(collector2)


