from pathlib import Path

import pytest

from xindy import __version__, cli


DATA_DIR = Path(__file__).resolve().parent / "data"


def test_version_option_outputs_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_cli_generates_expected_output(tmp_path):
    raw = DATA_DIR / "simple.raw"
    style = DATA_DIR / "simple.xdy"
    expected = (DATA_DIR / "simple.ind").read_text()
    out_path = tmp_path / "out.ind"

    code = cli.main(["-M", str(style), "-o", str(out_path), str(raw)])

    assert code == 0
    assert out_path.read_text() == expected


def test_cli_defaults_to_stdout_when_no_output(capsys):
    raw = DATA_DIR / "simple.raw"
    # relies on auto-resolving <raw>.xdy in same directory
    expected = (DATA_DIR / "simple.ind").read_text()

    code = cli.main([str(raw)])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == expected
