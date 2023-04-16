import pytest
from unittest.mock import MagicMock
import moderngl
from src.auraboros.shader import Shader2D


@pytest.fixture
def mock_ctx(mocker):
    mock_ctx = MagicMock(spec=moderngl.Context)
    mocker.patch('moderngl.create_context', return_value=mock_ctx)
    return mock_ctx


def test_shader_singleton(mock_ctx):
    shader1 = Shader2D()
    shader2 = Shader2D()
    assert shader1 is shader2
    shader1.test_attr = "test"
    assert shader2.test_attr is shader1.test_attr
