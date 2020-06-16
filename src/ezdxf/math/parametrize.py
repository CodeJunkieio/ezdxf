# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import List, Iterable, Sequence
import math
from ezdxf.math import Vector
from ezdxf.lldxf.const import DXFValueError
from .bezier4p import tangents_cubic_bezier_interpolation


def create_t_vector(fit_points: List[Vector], method: str) -> Iterable[float]:
    if method == 'uniform':
        return uniform_t_vector(len(fit_points))  # equally spaced 0 .. 1
    elif method in ('distance', 'chord'):
        return distance_t_vector(fit_points)
    elif method in ('centripetal', 'sqrt_chord'):
        return centripetal_t_vector(fit_points)
    else:
        raise DXFValueError('Unknown method: {}'.format(method))


def uniform_t_vector(length: int) -> Iterable[float]:
    n = float(length - 1)
    for t in range(length):
        yield float(t) / n


def distance_t_vector(fit_points: List[Vector]) -> Iterable[float]:
    distances = [p1.distance(p2) for p1, p2 in zip(fit_points, fit_points[1:])]
    yield from _normalize_distances(distances)


def centripetal_t_vector(fit_points: List[Vector]) -> Iterable[float]:
    distances = [math.sqrt(p1.distance(p2)) for p1, p2 in zip(fit_points, fit_points[1:])]
    yield from _normalize_distances(distances)


def _normalize_distances(distances: Sequence[float]) -> Iterable[float]:
    total_length = sum(distances)
    s = 0.0
    yield s
    for d in distances:
        s += d
        yield s / total_length


def estimate_tangents(points: List[Vector], method: str = '5-points') -> List[Vector]:
    """
    Estimate tangents for curve defined by given fit points.
    Calculated tangents are normalized (unit-vectors).

    Available tangent estimation methods:

        - "3-points": 3 point interpolation
        - "5-points": 5 point interpolation
        - "cubic-bezier": tangents from an interpolated cubic bezier curve
        - "diff": finite difference

    Args:
        points: start-, end- and passing points of curve
        method: tangent estimation method

    Returns:
        tangents as list of :class:`Vector` objects

    """
    if method == 'cubic-bezier':
        return tangents_cubic_bezier_interpolation(points, normalize=True)
    elif method.startswith('3-p'):
        return tangents_3_point_interpolation(points)
    elif method.startswith('5-p'):
        return tangents_5_point_interpolation(points)
    elif method.startswith('diff'):
        return finite_difference_interpolation(points)
    else:
        raise ValueError(f'Unknown method: {method}')


def tangents_3_point_interpolation(fit_points: List[Vector], method: str = 'chord') -> List[Vector]:
    q = [Q1 - Q0 for Q0, Q1 in zip(fit_points, fit_points[1:])]
    t = list(create_t_vector(fit_points, method))
    delta_t = [t1 - t0 for t0, t1 in zip(t, t[1:])]
    d = [qk / dtk for qk, dtk in zip(q, delta_t)]
    alpha = [dt0 / (dt0 + dt1) for dt0, dt1 in zip(delta_t, delta_t[1:])]
    tangents = [0.0]  # placeholder
    tangents.extend([(1.0 - alpha[k]) * d[k] + alpha[k] * d[k + 1] for k in range(len(d) - 1)])
    tangents[0] = 2.0 * d[0] - tangents[1]
    tangents.append(2.0 * d[-1] - tangents[-1])
    return [tangent.normalize() for tangent in tangents]


def tangents_5_point_interpolation(fit_points: List[Vector]) -> List[Vector]:
    n = len(fit_points)
    q = _delta_q(fit_points)

    alpha = list()
    for k in range(n):
        v1 = (q[k - 1].cross(q[k])).magnitude
        v2 = (q[k + 1].cross(q[k + 2])).magnitude
        alpha.append(v1 / (v1 + v2))

    tangents = []
    for k in range(n):
        vk = (1.0 - alpha[k]) * q[k] + alpha[k] * q[k + 1]
        tangents.append(vk.normalize())
    return tangents


def _delta_q(points: List[Vector]) -> List[Vector]:
    n = len(points)
    q = [0.0]  # placeholder
    q.extend([points[k + 1] - points[k] for k in range(n - 1)])
    q[0] = 2.0 * q[1] - q[2]
    q.append(2.0 * q[n - 1] - q[n - 2])  # q[n]
    q.append(2.0 * q[n] - q[n - 1])  # q[n+1]
    q.append(2.0 * q[0] - q[1])  # q[-1]
    return q


def finite_difference_interpolation(fit_points: List[Vector], normalize=True) -> List[Vector]:
    f = 2.0
    p = fit_points

    t = [(p[1] - p[0]) / f]
    for k in range(1, len(fit_points) - 1):
        t.append((p[k] - p[k - 1]) / f + (p[k + 1] - p[k]) / f)
    t.append((p[-1] - p[-2]) / f)
    if normalize:
        t = [v.normalize() for v in t]
    return t


def cardinal_interpolation(fit_points: List[Vector], tension: float) -> List[Vector]:
    # https://en.wikipedia.org/wiki/Cubic_Hermite_spline
    def tangent(p0, p1):
        return (p0 - p1).normalize(1.0 - tension)

    t = [tangent(fit_points[0], fit_points[1])]
    for k in range(1, len(fit_points) - 1):
        t.append(tangent(fit_points[k + 1], fit_points[k - 1]))
    t.append(tangent(fit_points[-1], fit_points[-2]))
    return t