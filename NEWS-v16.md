Version 0.16 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-16.html
- NEW: `ezdxf.render.make_path()` factory function to create `Path()` objects 
  from many DXF entities.
- NEW: `ezdxf.render.has_path_support()` to check if an entity is supported by 
  `make_path()`
- NEW: support module `disassemble`, see [docs](https://ezdxf.mozman.at/docs/disassemble.html)
- NEW: support module `bbox`, see [docs](https://ezdxf.mozman.at/docs/bbox.html)
- NEW: get clipping path from VIEWPORT entities by `make_path()`
- DEPRECATED: `Path.from_lwpolyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_polyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_spline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_ellipse()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_arc()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_circle()`, replaced by factory `make_path()`
