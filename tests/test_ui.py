from src.auraboros.ui import UI, UIFlowLayout


class ExampleUI(UI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calc_real_size = self._calc_real_size

    def _calc_real_size(self):
        return [32, 32]


class TestUIFlowLayout:
    def test_relocate_children(self):
        layout1 = UIFlowLayout(orientation="vertical", pos=[0, 0])
        layout1.add_child(ExampleUI())
        layout1.add_child(ExampleUI())
        layout1.add_child(ExampleUI())
        assert layout1.children[0].pos == [0, 0]
        assert layout1.children[1].pos == [0, 32]
        assert layout1.children[2].pos == [0, 64]
