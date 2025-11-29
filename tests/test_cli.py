import pytest

from xindy import __version__, cli


def test_version_option_outputs_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_cli_rejects_positional_files():
    with pytest.raises(SystemExit):
        cli.main(["input.raw"])
