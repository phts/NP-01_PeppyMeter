# Copyright 2016-2022 PeppyMeter peppy.player@gmail.com
#
# This file is part of PeppyMeter.
#
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

import time

from threading import Thread


class ChannelLevel:
    def __init__(self, fall_speed):
        self.level = 0.0
        self.fall_speed = fall_speed

    def tick(self, level):
        if level > self.level:
            self.level = level
        else:
            self.level = self.level - self.fall_speed
        return self.level


class LinearAnimator(Thread):
    """Provides linear animation in a separate thread"""

    def __init__(self, data_source, components, base, ui_refresh_period, origin_y, fall_speed):
        """Initializer

        :param data_source: data source
        :param components: UI component
        :param base: meter base
        :param ui_refresh_period: animation interval
                :param origin_y: origin Y
        """
        Thread.__init__(self)
        self.index = 0
        self.data_source = data_source
        self.components = components
        self.origin_y = origin_y
        self.comp_width, self.comp_height = components[1].content[1].get_size()
        self.run_flag = True
        self.base = base
        self.ui_refresh_period = ui_refresh_period
        self.bgr = self.base.bgr
        self.fgr = self.base.fgr
        self.left_meter = ChannelLevel(fall_speed)
        self.right_meter = ChannelLevel(fall_speed)

    def run(self):
        """Thread method. Converts volume value into the mask width and displays corresponding mask."""

        previous_rect_left = self.components[1].bounding_box.copy()
        previous_rect_right = self.components[2].bounding_box.copy()
        previous_volume_left = previous_volume_right = 0.0

        while self.run_flag:
            d = self.data_source.get_current_data()

            try:
                left_level = self.left_meter.tick(d[0])
                right_level = self.right_meter.tick(d[1])
                previous_rect_left, previous_volume_left = self.update_channel(
                    left_level, self.components[1], previous_rect_left, previous_volume_left
                )
                previous_rect_right, previous_volume_right = self.update_channel(
                    right_level, self.components[2], previous_rect_right, previous_volume_right
                )
            except:
                pass

            time.sleep(self.ui_refresh_period)

    def stop_thread(self):
        self.run_flag = False
        time.sleep(self.ui_refresh_period * 2)

    def update_channel(self, volume, component, previous_rect, previous_volume):
        if previous_volume == volume:
            return (previous_rect, previous_volume)

        self.base.draw_bgr_fgr(previous_rect, self.base.bgr)

        n = int((volume * self.base.max_volume) / (self.base.step * 100))
        if n >= len(self.base.masks):
            n = len(self.base.masks) - 1
        w = self.base.masks[n]
        if w == 0:
            w = 1

        if self.comp_width > self.comp_height:
            component.bounding_box.w = w
            component.bounding_box.x = 0
            component.bounding_box.y = 0
        else:
            component.bounding_box.h = w
            component.bounding_box.x = 0
            component.bounding_box.y = self.comp_height - w
            component.content_y = self.origin_y + self.comp_height - w

        component.draw()

        r = component.bounding_box.copy()
        r.x = component.content_x
        r.y = component.content_y
        u = previous_rect.union(r)
        if self.base.fgr:
            self.base.draw_bgr_fgr(u.copy(), self.base.fgr)

        self.base.update_rectangle(u)

        return (r.copy(), volume)
