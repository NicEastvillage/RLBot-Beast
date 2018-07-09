import math
import situation
from situation import Data
from vec import Vec3


GRAVITY = Vec3(z=-650)


def move_body(body, time, gravity=True):
    acc = GRAVITY if gravity else Vec3()

    # (1/2 * a * t^2) + (v * t) + p
    new_loc = 0.5 * time * time * acc + time * body.velocity + body.location
    new_vel = time * acc + body.velocity
    body.location = new_loc
    body.velocity = new_vel

    return body


def next_wall_hit(body, offset=0):
    wall_hits = [
        max((situation.ARENA_WIDTH2-offset - body.location.x) / body.velocity.x, 0) if body.velocity.x != 0 else 1e307,
        max((situation.ARENA_WIDTH2-offset + body.location.x) / -body.velocity.x, 0) if body.velocity.x != 0 else 1e307,
        max((situation.ARENA_LENGTH2-offset - body.location.y) / body.velocity.y, 0) if body.velocity.y != 0 else 1e307,
        max((situation.ARENA_LENGTH2-offset + body.velocity.y) / -body.velocity.y, 0) if body.velocity.y != 0 else 1e307
    ]
    wall_index = -1
    earliest_hit = 1e306
    for i, hit_time in enumerate(wall_hits):
        if hit_time <= earliest_hit:
            earliest_hit = hit_time
            wall_index = i

    return dict(hit=wall_index != -1,
                time=earliest_hit,
                side=wall_index == 0 or wall_index == 1)
