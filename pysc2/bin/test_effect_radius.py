from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest
from absl.testing import parameterized
from pysc2.lib import units
from pysc2.tests import utils


# Tests for effects. Please use it in latest deepmind's pysc2
class ObsTest(parameterized.TestCase, utils.GameReplayTestCase):

  @parameterized.named_parameters(
    ("BlindingCloud", [499, 2063]),
    ("CorrosiveBile", [688, 2338]),
    ("LurkerSpines", [503, None]),
  )
  def test(self, unit_ability):
    unit_type, ability_id = unit_ability
    @utils.GameReplayTestCase.setup()
    def test_effects(self):
      def get_effect_proto(obs, effect_id):
        for e in obs.observation.raw_data.effects:
          if e.effect_id == effect_id:
            return e
        return None

      data_raw = self._controllers[0].data_raw()

      self.god()
      self.move_camera(32, 32)

      # Create some sentries.
      self.create_unit(unit_type=units.Zerg.Ultralisk, owner=2, pos=(30, 30))
      self.create_unit(unit_type=unit_type, owner=1, pos=(28, 30))

      self.step()
      obs = self.observe()

      # Give enough energy.
      unit = utils.get_unit(obs[0], unit_type=unit_type)
      ultralisk = utils.get_unit(obs[1], unit_type=units.Zerg.Ultralisk)
      self.set_energy(unit.tag, 200)

      self.step()
      obs = self.observe()

      if ability_id:
        ability = [ab for ab in data_raw.abilities if ab.ability_id == ability_id][0]

        if ability.target == 3: # Target.Unit
          self.raw_unit_command(0, ability_id, unit.tag, target=ultralisk.tag)
        else:
          self.raw_unit_command(0, ability_id, unit.tag, pos=[ultralisk.pos.x, ultralisk.pos.y])

      for i in range(8):
        self.step(8)
        obs = self.observe()
        if len(obs[0].observation.raw_data.effects) > 0:
          print(obs[0].observation.raw_data.effects)
          print(obs[1].observation.raw_data.effects)
          break


    test_effects(self)


if __name__ == "__main__":
  absltest.main()
