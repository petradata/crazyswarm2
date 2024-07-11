from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
from rclpy.node import Node
import rowan

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
        self.ts = []
        self.all_states = []
        self.all_states_desired = []
        self.all_actions = []
        self.filename = params['output_file']
        self.anim = Animation()

    def step(self, t, states: list[State], states_desired: list[State], actions: list[Action]):
        self.ts.append(t)
        self.all_states.append(copy.deepcopy(states))
        self.all_states_desired.append(copy.deepcopy(states_desired))
        self.all_actions.append(copy.deepcopy(actions))

    def shutdown(self):

        vis = meshcat.Visualizer()

        vis["/Cameras/default"].set_transform(
            tf.translation_matrix([0, 0, 0]).dot(
            tf.euler_matrix(0, np.radians(-30), -np.pi/2)))

        vis["/Cameras/default/rotated/<object>"].set_transform(
            tf.translation_matrix([1, 0, 0]))

        for k, name in enumerate(self.names):
            vis[name].set_object(
                g.ObjMeshGeometry.from_file(str(Path(__file__).resolve().parent/ "data" / "model" / "cf.obj")))

        anim = Animation()

        for idx, t in enumerate(self.ts):
            with anim.at_frame(vis, t) as frame:
                for k, name in enumerate(self.names):

                    s = self.all_states[idx][k]

                    frame[name].set_transform(
                        tf.translation_matrix(s.pos).dot(
                            tf.quaternion_matrix(s.quat)))
            # time.sleep(0.1)
        vis.set_animation(anim)
        res = vis.static_html()
        # save to a file
        with open(self.filename, "w") as f:
            f.write(res)
