from aiu import __version__
from aiu.cli import main


def test_version(capsys):
    try:
        main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()
    assert f"aiu {__version__}" in captured.out
