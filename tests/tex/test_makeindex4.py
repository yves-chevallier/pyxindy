import io
import sys

from xindy.tex import makeindex4_main


def test_makeindex4_cli_produces_index(tmp_path):
    idx = tmp_path / "sample.idx"
    idx.write_text(
        "\\indexentry{alpha}{1}\n\\indexentry{alpha }{2}\n\\indexentry{beta|imp}{3}\n",
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


def test_makeindex4_cli_reads_stdin(tmp_path, monkeypatch):
    idx_text = "\\indexentry{alpha}{1}\\n\\indexentry{beta}{2}\\n"
    stdin = io.TextIOWrapper(io.BytesIO(idx_text.encode("latin-1")), encoding="latin-1")
    monkeypatch.setattr(sys, "stdin", stdin)

    out_path = tmp_path / "stdin.ind"
    log_path = tmp_path / "stdin.ilg"

    code = makeindex4_main(["-i", "-o", str(out_path), "-t", str(log_path)])

    assert code == 0
    output = out_path.read_text()
    assert "alpha" in output and "beta" in output
    assert log_path.read_text().strip().startswith("Processed 2 entries")


def test_makeindex4_cli_multiple_inputs(tmp_path):
    idx1 = tmp_path / "a.idx"
    idx2 = tmp_path / "b.idx"
    idx1.write_text("\\indexentry{alpha}{1}\n", encoding="latin-1")
    idx2.write_text("\\indexentry{beta}{2}\n", encoding="latin-1")
    out_path = tmp_path / "multi.ind"
    log_path = tmp_path / "multi.ilg"

    code = makeindex4_main([str(idx1), str(idx2), "-o", str(out_path), "-t", str(log_path)])

    assert code == 0
    output = out_path.read_text()
    assert "alpha" in output and "beta" in output
    assert log_path.read_text().strip().startswith("Processed 2 entries")


def test_makeindex4_cli_no_range_flag(tmp_path):
    idx = tmp_path / "range.idx"
    idx.write_text(
        "\\indexentry{alpha}{1}\n\\indexentry{alpha}{2}\n\\indexentry{alpha}{3}\n",
        encoding="latin-1",
    )
    out_path = tmp_path / "range.ind"
    log_path = tmp_path / "range.ilg"

    code = makeindex4_main([str(idx), "-o", str(out_path), "-t", str(log_path)])

    assert code == 0
    assert "--" in out_path.read_text()

    out_path_no = tmp_path / "range-no.ind"
    log_path_no = tmp_path / "range-no.ilg"

    code = makeindex4_main([str(idx), "-o", str(out_path_no), "-t", str(log_path_no), "-r"])

    assert code == 0
    output = out_path_no.read_text()
    assert "--" not in output
    assert "1" in output and "2" in output and "3" in output


def test_makeindex4_cli_start_page(tmp_path):
    idx = tmp_path / "start.idx"
    idx.write_text("\\indexentry{alpha}{1}\n", encoding="latin-1")
    out_path = tmp_path / "start.ind"
    log_path = tmp_path / "start.ilg"

    code = makeindex4_main([str(idx), "-o", str(out_path), "-t", str(log_path), "-p", "5"])

    assert code == 0
    assert "\\setcounter{page}{5}" in out_path.read_text()


def test_makeindex4_cli_xdy_style(tmp_path):
    idx = tmp_path / "style.idx"
    idx.write_text("\\indexentry{alpha}{1}\n\\indexentry{alpha}{2}\n", encoding="latin-1")
    style = tmp_path / "custom.xdy"
    style.write_text('(markup-locref-list :sep "; ")\n', encoding="utf-8")
    out_path = tmp_path / "style.ind"
    log_path = tmp_path / "style.ilg"

    code = makeindex4_main(
        [
            str(idx),
            "-o",
            str(out_path),
            "-t",
            str(log_path),
            "-s",
            str(style),
            "-r",
        ]
    )

    assert code == 0
    output = out_path.read_text()
    assert "; " in output


def test_makeindex4_cli_ist_style(tmp_path):
    idx = tmp_path / "ist.idx"
    idx.write_text("\\indexentry{alpha}{1}\n\\indexentry{alpha}{2}\n", encoding="latin-1")
    style = tmp_path / "custom.ist"
    style.write_text(
        'preamble "\\\\begin{theindex}\\n"\n'
        'postamble "\\\\end{theindex}\\n"\n'
        'delim_n "; "\n'
        'item_0 "\\\\item "\n',
        encoding="latin-1",
    )
    out_path = tmp_path / "ist.ind"
    log_path = tmp_path / "ist.ilg"

    code = makeindex4_main(
        [
            str(idx),
            "-o",
            str(out_path),
            "-t",
            str(log_path),
            "-s",
            str(style),
            "-r",
        ]
    )

    assert code == 0
    output = out_path.read_text()
    assert "\\begin{theindex}" in output
    assert "\\end{theindex}" in output
    assert "; " in output


def test_makeindex4_cli_quiet_suppresses_style_warning(tmp_path, capsys):
    idx = tmp_path / "quiet.idx"
    idx.write_text("\\indexentry{alpha}{1}\n", encoding="latin-1")
    style = tmp_path / "custom.ist"
    style.write_text('unknown_key "ignored"\n', encoding="latin-1")
    out_path = tmp_path / "quiet.ind"
    log_path = tmp_path / "quiet.ilg"

    code = makeindex4_main(
        [
            str(idx),
            "-o",
            str(out_path),
            "-t",
            str(log_path),
            "-s",
            str(style),
            "-q",
        ]
    )

    assert code == 0
    captured = capsys.readouterr()
    assert captured.err == ""
