from RLUtilities.Maneuvers import AirDodge


class DodgePlan:
    def __init__(self, bot, target=None):
        self.target = target
        self.dodge = AirDodge(bot.info.my_car, target=self._resolve_target())
        self.finished = False

    def _resolve_target(self):
        return self.target() if callable(self.target) else self.target

    def execute(self, bot):
        self.dodge.target = self._resolve_target()
        self.dodge.step(0.01666)
        bot.controls = self.dodge.controls
        self.finished = self.dodge.finished
