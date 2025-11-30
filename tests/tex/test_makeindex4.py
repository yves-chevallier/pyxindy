from pathlib import Path

from xindy.tex import makeindex4_main


def test_makeindex4_cli_produces_index(tmp_path):
    idx = tmp_path / "sample.idx"
    idx.write_text(
        "\\indexentry{alpha}{1}\n"
        "\\indexentry{alpha }{2}\n"
        "\\indexentry{beta|imp}{3}\n",
        encoding="latin-1",
    )
    ind_path = tmp_path / "sample.ind"
    log_path = tmp_path / "sample.ilg"

    code = makeindex4_main(
        [
            str(idx),
            "-o",
            str(ind_path),
            "-t",
            str(log_path),
            "-c",
        ]
    )

    assert code == 0
    output = ind_path.read_text()
    assert "\\begin{theindex}" in output
    assert "alpha" in output and "1" in output and "2" in output
    assert "\\imp{3}" in output
    assert log_path.read_text().strip().startswith("Processed 3 entries")
