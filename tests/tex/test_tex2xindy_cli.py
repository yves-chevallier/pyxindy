from tests_paths import XINDY_TESTS_DIR as TESTS_DIR
from xindy.raw.reader import load_raw_index
from xindy.tex import tex2xindy


def test_tex2xindy_cli_writes_expected_raw(tmp_path, capsys):
    idx_path = TESTS_DIR / "infII.idx"
    out_path = tmp_path / "out.raw"
    log_path = tmp_path / "log.txt"

    code = tex2xindy.main(
        [
            str(idx_path),
            "-o",
            str(out_path),
            "--log",
            str(log_path),
            "--input-encoding",
            "latin-1",
            "--output-encoding",
            "utf-8",
        ]
    )

    assert code == 0
    expected = load_raw_index(TESTS_DIR / "infII.raw")
    produced = load_raw_index(out_path)
    expected_set = {(e.key, e.attr, e.locref) for e in expected}
    produced_set = {(e.key, e.attr, e.locref) for e in produced}
    assert expected_set == produced_set
    assert "converted" in log_path.read_text()


def test_tex2xindy_cli_stdout(capsys):
    idx_path = TESTS_DIR / "infII.idx"
    code = tex2xindy.main([str(idx_path), "--input-encoding", "latin-1"])
    assert code == 0
    captured = capsys.readouterr()
    assert "(indexentry" in captured.out
