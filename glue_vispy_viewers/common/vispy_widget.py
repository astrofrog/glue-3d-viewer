from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from ..extern.vispy import scene
from .axes import AxesVisual3D

from matplotlib.colors import ColorConverter

from glue.config import settings
from glue.utils.qt import get_qapp

rgb = ColorConverter().to_rgb

LIMITS_PROPS = [coord + attribute for coord in 'xyz' for attribute in ['_min', '_max', '_stretch']]


class VispyWidgetHelper(object):

    def __init__(self, parent=None, viewer_state=None):

        # Prepare Vispy canvas. We set the depth_size to 24 to avoid issues
        # with isosurfaces on MacOS X
        self.canvas = scene.SceneCanvas(keys=None, show=False,
                                        config={'depth_size': 24},
                                        bgcolor=rgb(settings.BACKGROUND_COLOR))

        # Set up a viewbox
        self.view = self.canvas.central_widget.add_view()
        self.view.parent = self.canvas.scene

        # Set whether we are emulating a 3D texture. This needs to be enabled
        # as a workaround on Windows otherwise VisPy crashes.
        self.emulate_texture = (sys.platform == 'win32' and
                                sys.version_info[0] < 3)

        self.scene_transform = scene.STTransform()
        self.limit_transforms = {}

        fc = rgb(settings.FOREGROUND_COLOR)

        self.axis = AxesVisual3D(axis_color=fc, tick_color=fc, text_color=fc,
                                 tick_width=1, minor_tick_length=2,
                                 major_tick_length=4, axis_width=0,
                                 tick_label_margin=10, axis_label_margin=25,
                                 tick_font_size=6, axis_font_size=8,
                                 view=self.view,
                                 transform=self.scene_transform)

        # Create a turntable camera. For now, this is the only camerate type
        # we support, but if we support more in future, we should implement
        # that here

        # Orthographic perspective view as default
        self.view.camera = scene.cameras.TurntableCamera(parent=self.view.scene,
                                                         fov=0., distance=4.0)

        # We need to call render here otherwise we'll later encounter an OpenGL
        # program validation error.
        # self.canvas.render()

        self.viewer_state = viewer_state
        self.viewer_state.add_callback('*', self._update_from_state, echo_name=True)

    def _update_appearance_from_settings(self):
        self.canvas.bgcolor = rgb(settings.BACKGROUND_COLOR)
        self.axis.axis_color = rgb(settings.FOREGROUND_COLOR)
        self.axis.tick_color = rgb(settings.FOREGROUND_COLOR)
        self.axis.label_color = rgb(settings.FOREGROUND_COLOR)

    def add_data_visual(self, visual):
        self.limit_transforms[visual] = scene.STTransform()
        visual.transform = self.limit_transforms[visual]
        self.view.add(visual)

    def _update_from_state(self, prop, value):

        if 'visible_axes' in prop:

            if self.viewer_state.visible_axes:
                self.axis.xlim = self.viewer_state.x_min, self.viewer_state.x_max
                self.axis.ylim = self.viewer_state.y_min, self.viewer_state.y_max
                self.axis.zlim = self.viewer_state.z_min, self.viewer_state.z_max
                self.axis.parent = self.view.scene
            else:
                self.axis.parent = None

        if 'perspective_view' in prop:

            if self.viewer_state.perspective_view:
                self.view.camera.fov = 30
                self.axis.tick_font_size = 28
                self.axis.axis_font_size = 35
            else:
                self.view.camera.fov = 0
                self.axis.tick_font_size = 6
                self.axis.axis_font_size = 8

        if 'x_att' in prop:
            self.axis.xlabel = self.viewer_state.x_att[0].label

        if 'y_att' in prop:
            self.axis.ylabel = self.viewer_state.y_att[0].label

        if 'z_att' in prop:
            self.axis.zlabel = self.viewer_state.z_att[0].label

        if 'x_stretch' in prop or 'y_stretch' in prop or 'z_stretch' in prop or 'native_aspect' in prop:
            self.scene_transform.scale = (self.viewer_state.x_stretch * self.viewer_state.aspect[0],
                                          self.viewer_state.y_stretch * self.viewer_state.aspect[1],
                                          self.viewer_state.z_stretch * self.viewer_state.aspect[2])

        if any(p in prop for p in LIMITS_PROPS) or 'native_aspect' in prop:

            scale = [2 / (self.viewer_state.x_max - self.viewer_state.x_min) *
                     self.viewer_state.x_stretch * self.viewer_state.aspect[0],
                     2 / (self.viewer_state.y_max - self.viewer_state.y_min) *
                     self.viewer_state.y_stretch * self.viewer_state.aspect[1],
                     2 / (self.viewer_state.z_max - self.viewer_state.z_min) *
                     self.viewer_state.z_stretch * self.viewer_state.aspect[2]]

            translate = [-0.5 * (self.viewer_state.x_min + self.viewer_state.x_max) * scale[0],
                         -0.5 * (self.viewer_state.y_min + self.viewer_state.y_max) * scale[1],
                         -0.5 * (self.viewer_state.z_min + self.viewer_state.z_max) * scale[2]]

            for visual in self.limit_transforms:
                self.limit_transforms[visual].scale = scale
                self.limit_transforms[visual].translate = translate

            self.axis.xlim = self.viewer_state.x_min, self.viewer_state.x_max
            self.axis.ylim = self.viewer_state.y_min, self.viewer_state.y_max
            self.axis.zlim = self.viewer_state.z_min, self.viewer_state.z_max

        self.canvas.update()

    def _reset_view(self):
        self.view.camera.reset()
        # update the cam.fov with checkbox
        self._toggle_perspective()


if __name__ == "__main__":

    from viewer_options import VispyOptionsWidget

    app = get_qapp()
    w = VispyWidgetHelper()
    d = VispyOptionsWidget(vispy_widget=w)
    d.show()

    positions = np.random.random((1000, 3))
    scat_visual = scene.visuals.Markers()
    scat_visual.set_data(positions, symbol='disc', edge_color=None, face_color='red')
    w.add_data_visual(scat_visual)

    d.x_min = 0
    d.x_max = +1

    d.y_min = 0
    d.y_max = +1

    d.z_min = 0
    d.z_max = +1

    w.show()
    app.exec_()
    app.quit()
