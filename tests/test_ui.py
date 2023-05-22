from src.auraboros.ui import UI


class ExampleUI(UI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self):
        return [32, 32]
