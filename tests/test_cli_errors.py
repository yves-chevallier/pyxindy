from pathlib import Path

from xindy import cli


TESTS_DIR = Path(__file__).resolve().parents[1] / "xindy-src" / "xindy-2.1" / "tests"


def _dummy_raw(tmp_path: Path) -> Path:
    raw = tmp_path / "dummy.raw"
    raw.write_text('(indexentry :key ("foo") :locref "1")\n', encoding="utf-8")
    return raw


def test_cli_reports_parse_error(tmp_path, capsys):
    raw = _dummy_raw(tmp_path)
    log = tmp_path / "err1.xlg"

    code = cli.main(["-M", str(TESTS_DIR / "err1.xdy"), "-l", str(log), str(raw)])

    captured = capsys.readouterr()
    assert code == 1
    assert "xindy error" in captured.err
    assert log.exists()


def test_cli_reports_eval_error(tmp_path, capsys):
    raw = _dummy_raw(tmp_path)
    log = tmp_path / "err2.xlg"

    code = cli.main(["-M", str(TESTS_DIR / "err2.xdy"), "-l", str(log), str(raw)])

    captured = capsys.readouterr()
    assert code == 1
    assert "xindy error" in captured.err
    assert log.exists()
