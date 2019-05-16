from pathlib import Path

from morelia.config import TOMLConfig
from morelia.formatters import (
    Buffered,
    FileOutput,
    RemoteOutput,
    TerminalOutput,
    TextFormat,
)

fixtures_dir = Path(__file__).parent / "fixtures"


def test_creates_writers():
    config = TOMLConfig("terminals", filename=fixtures_dir / "example_pyproject.toml")
    writers = config.get_writers()
    assert writers == [
        TextFormat(TerminalOutput(dest="stderr")),
        TextFormat(TerminalOutput(dest="stdout")),
        TextFormat(TerminalOutput(), color=True),
        TextFormat(Buffered(FileOutput(path="terminal.log"))),
        TextFormat(FileOutput(path="terminal.log")),
        TextFormat(Buffered(RemoteOutput(url="http://example.com/terminal.log"))),
        TextFormat(RemoteOutput(url="http://example.com/terminal.log")),
    ]


def test_does_not_create_writers_when_config_files_does_not_exist():
    config = TOMLConfig("terminals", filename=fixtures_dir / "not_existing.toml")
    writers = config.get_writers()
    assert writers == []
