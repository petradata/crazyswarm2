from __future__ import annotations

from pathlib import Path

import numpy as np
from rclpy.node import Node

# visualization related
import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
from meshcat.animation import Animation

from ..sim_data_types import Action, State


class Visualization:
    """Creates static HTML file animation using meshcat"""

    def __init__(self, node: Node, params: dict, names: list[str], states: list[State]):
        self.node = node
        self.names = names
        self.filename = params['output_file']

        self.vis = meshcat.Visualizer()

        self.vis["/Cameras/default"].set_transform(
            tf.translation_matrix([0, 0, 0]).dot(
            tf.euler_matrix(0, np.radians(-30), -np.pi/2)))

        self.vis["/Cameras/default/rotated/<object>"].set_transform(
            tf.translation_matrix([1, 0, 0]))

        for k, name in enumerate(self.names):
            self.vis[name].set_object(
                g.ObjMeshGeometry.from_file(str(Path(__file__).resolve().parent/ "data" / "model" / "cf.obj")))

        self.anim = Animation(default_framerate=1.0)
        self.start_time = None

    def step(self, t, states: list[State], states_desired: list[State], actions: list[Action]):
        if self.start_time is None:
            self.start_time = t
        with self.anim.at_frame(self.vis, t - self.start_time) as frame:
            for k, name in enumerate(self.names):
                s = states[k]
                frame[name].set_transform(
                    tf.translation_matrix(s.pos).dot(
                        tf.quaternion_matrix(s.quat)))

    def shutdown(self):
        self.vis.set_animation(self.anim)
        res = self.vis.static_html()
        # save to a file
        with open(self.filename, "w") as f:
            f.write(res)
