import pytest

from xindy.dsl.sexpr import Keyword, SExprSyntaxError, Symbol, loads, parse_one


def test_parse_one_returns_nested_python_objects():
    expr = parse_one('(indexentry :key ("a" "b") :locref "1")')
    assert expr == [
        Symbol("indexentry"),
        Keyword("key"),
        ["a", "b"],
        Keyword("locref"),
        "1",
    ]


def test_comment_and_whitespace_are_ignored():
    text = """
    ; leading comment
    (foo 1 2)  ; inline comment
    #|
      block comment
    |#
    (bar "baz")
    """
    exprs = loads(text)
    assert len(exprs) == 2
    assert exprs[0][0] == Symbol("foo")
    assert exprs[1][0] == Symbol("bar")


def test_parse_one_detects_multiple_forms():
    with pytest.raises(SExprSyntaxError):
        parse_one("(foo) (bar)")


def test_unterminated_list_raises():
    with pytest.raises(SExprSyntaxError):
        parse_one("(foo (bar)")
