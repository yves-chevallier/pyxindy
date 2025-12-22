from xindy.tex import makeglossaries_main


def test_makeglossaries_accepts_stdin_flag(tmp_path):
    base = tmp_path / "doc"
    aux_path = base.with_suffix(".aux")
    aux_path.write_text("\\@istfilename{foo.ist}\n", encoding="utf-8")

    code = makeglossaries_main([str(base), "-i", "-q"])

    assert code == 0
