import pytest
import prompty
from pathlib import Path

BASE_PATH = str(Path(__file__).absolute().parent.as_posix())


def test_prompty_config_local():
    p = prompty.load(f"{BASE_PATH}/prompts/sub/sub/basic.prompty")
    assert p.model.configuration["type"] == "TEST_LOCAL"

def test_prompty_config_global():
    p = prompty.load(f"{BASE_PATH}/prompts/sub/basic.prompty")
    assert p.model.configuration["type"] == "azure"


def test_prompty_config_headless():
    p = prompty.headless("embedding", ["this is the first line", "this is the second line"])
    assert p.model.configuration["type"] == "FROM_CONTENT"

# make sure the prompty path is
# relative to the current executing file
def test_prompty_relative_local():
    from .prompts.test import run
    p = run()
    assert p.name == "Basic Prompt"


def test_prompty_relative():
    from .prompts.sub.sub.test import run
    p = run()
    assert p.name == "Prompt with complex context"
