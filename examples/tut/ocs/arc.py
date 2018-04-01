# Copyright (c) 2018 Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.algebra import UCS, Vector

dwg = ezdxf.new('R2010')
msp = dwg.modelspace()

# include-start
ucs = UCS(origin=(0, 2, 2), ux=(1, 0, 0), uz=(0, 1, 1))
msp.add_arc(
    center=ucs.ucs_to_ocs((0, 0)),
    radius=1,
    start_angle=ucs.ocs_angle_deg(45),  # shortcut
    end_angle=ucs.ocs_angle_deg(270),  # shortcut
    dxfattribs={
        'extrusion': ucs.uz,
        'color': 2,
    })
center = ucs.ucs_to_wcs((0, 0))
msp.add_line(
    start=center,
    end=ucs.ucs_to_wcs(Vector.from_deg_angle(45)),
    dxfattribs={'color': 2},
)
msp.add_line(
    start=center,
    end=ucs.ucs_to_wcs(Vector.from_deg_angle(270)),
    dxfattribs={'color': 2},
)
# include-end

ucs.render_axis(msp)
dwg.saveas('ocs_arc.dxf')
