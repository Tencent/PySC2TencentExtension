#!/usr/bin/python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Verify that the game renders rgb pixels."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest

import os
import numpy as np

from imageio import imwrite
from pysc2 import maps
from pysc2 import run_configs
from absl.testing import parameterized

from s2clientprotocol import common_pb2 as sc_common
from s2clientprotocol import sc2api_pb2 as sc_pb


def norm_img(img):
  return img if np.max(img) <= 1.0 else np.divide(img, 255.0)


def bitmap2array(image):
  bit_image_dtypes = {
    1: np.uint8,
    8: np.uint8,
    16: np.uint16,
    32: np.int32,
  }
  # array = np.array([a for a in image.data])
  data = np.frombuffer(image.data, bit_image_dtypes[image.bits_per_pixel])
  if image.bits_per_pixel == 1:
    data = np.unpackbits(data)
    if data.shape[0] != image.size.x * image.size.y:
      # This could happen if the correct length isn't a multiple of 8, leading
      # to some padding bits at the end of the string which are incorrectly
      # interpreted as data.
      data = data[:image.size.x * image.size.y]
  array = np.reshape(data, (image.size.y, image.size.x)).astype(np.int32)
  return array


class TestRender(parameterized.TestCase):

  @parameterized.named_parameters(
    ("4.7.1", '4.7.1'),
    ("4.8.0", '4.8.0'),
    ("4.8.2", '4.8.2'),
    ("4.8.3", '4.8.3'),
    ("4.8.4", '4.8.4'),
    ("4.8.6", '4.8.6'),
    ("4.9.0", '4.9.0'),
    ("4.9.1", '4.9.1'),
    ("4.9.2", '4.9.2'),
    ("4.9.3", '4.9.3'),
    ("4.10.0", '4.10.0'),
  )
  def test_render(self, version):
    interface = sc_pb.InterfaceOptions()
    interface.raw = True
    interface.score = True
    interface.feature_layer.width = 24
    interface.feature_layer.resolution.x = 256
    interface.feature_layer.resolution.y = 256
    interface.feature_layer.minimap_resolution.x = 152
    interface.feature_layer.minimap_resolution.y = 168
    interface.render.resolution.x = 256
    interface.render.resolution.y = 256
    interface.render.minimap_resolution.x = 128
    interface.render.minimap_resolution.y = 128

    # Delete this line in Mac
    # os.environ['SC2PATH'] = os.path.join('/root/', version)
    run_config = run_configs.get()
    with run_config.start(version=version) as controller:
      map_inst = maps.get("KairosJunction")
      create = sc_pb.RequestCreateGame(
          realtime=False, disable_fog=False,
          local_map=sc_pb.LocalMap(map_path=map_inst.path,
                                   map_data=map_inst.data(run_config)))
      create.player_setup.add(type=sc_pb.Participant, race=sc_common.Zerg)
      create.player_setup.add(
          type=sc_pb.Computer, race=sc_common.Zerg, difficulty=sc_pb.VeryEasy)
      join = sc_pb.RequestJoinGame(race=sc_common.Zerg, options=interface)
      controller.create_game(create)
      controller.join_game(join)

      controller.step(100)
      game_info = controller.game_info()
      observation = controller.observe()
      placement_grid = norm_img(
        bitmap2array(game_info.start_raw.placement_grid))
      pathing_grid = norm_img(bitmap2array(game_info.start_raw.pathing_grid))
      creep = norm_img(bitmap2array(observation.observation.raw_data.map_state.creep))
      # 0=Hidden, 1=Fogged, 2=Visible, 3=FullHidden
      visibility = bitmap2array(observation.observation.raw_data.map_state.visibility)
      visibility = np.equal(visibility, 2)

      creep_minimap = bitmap2array(observation.observation.feature_layer_data.minimap_renders.creep)
      creep_minimap = norm_img(np.array(creep_minimap, np.int32))
      height_map = bitmap2array(observation.observation.feature_layer_data.minimap_renders.height_map)
      height_map = norm_img(np.array(height_map, np.int32))
      visibility_minimap = bitmap2array(observation.observation.feature_layer_data.minimap_renders.visibility_map)
      visibility_minimap = np.equal(visibility_minimap, 2)


      imwrite('images/' + version + '_creep.jpg', creep.astype(np.float32))
      imwrite('images/' + version + '_placement_grid.jpg', placement_grid.astype(np.float32))
      imwrite('images/' + version + '_pathing_grid.jpg', pathing_grid.astype(np.float32))
      imwrite('images/' + version + '_visibility.jpg', visibility.astype(np.float32))
      imwrite('images/' + version + '_creep_minimap.jpg', creep_minimap.astype(np.float32))
      imwrite('images/' + version + '_height_map.jpg', height_map.astype(np.float32))
      imwrite('images/' + version + '_visibility_minimap.jpg', visibility_minimap.astype(np.float32))

if __name__ == "__main__":
  absltest.main()
