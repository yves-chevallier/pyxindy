from xindy.locref import (
    Alphabet,
    Enumeration,
    LocClassLayer,
    LocClassSeparator,
    build_location_reference,
    checked_make_standard_location_class,
    locref_class_eq,
    locref_class_lt,
    locref_ordnum_lt,
    make_category_attribute,
    perform_match,
    prefix_match_for_radix_numbers,
)


def make_digit_enumeration() -> Enumeration:
    return Enumeration(
        name="arabic-numbers",
        base_alphabet=tuple("0123456789"),
        match_func=lambda text: prefix_match_for_radix_numbers(text, 10),
    )


def test_alphabet_prefix_match_prefers_longest_symbol():
    alph = Alphabet(name="custom", symbols=("1", "10", "101"))
    result = alph.prefix_match("101A")
    assert result
    assert result.matched == "101"
    assert result.rest == "A"
    assert result.ordnum == 2


def test_perform_match_handles_separators():
    digits = make_digit_enumeration()
    layers = [
        LocClassLayer(digits),
        LocClassSeparator("-"),
        LocClassLayer(digits),
    ]
    loccls = checked_make_standard_location_class("page-range", layers, join_length=2)
    matched, ordnums = perform_match("12-34", loccls)
    assert matched == ["12", "34"]
    assert ordnums == [12, 34]


def test_build_location_reference_returns_none_on_failure():
    digits = make_digit_enumeration()
    loccls = checked_make_standard_location_class(
        "page",
        [LocClassLayer(digits)],
        join_length=2,
    )
    category = make_category_attribute("definition")
    ref = build_location_reference(loccls, "12", category, "def")
    assert ref is not None
    assert ref.layers == ("12",)
    bad = build_location_reference(loccls, "AB", category, "def")
    assert bad is None


def test_locref_comparisons():
    digits = make_digit_enumeration()
    loccls = checked_make_standard_location_class(
        "pages",
        [LocClassLayer(digits)],
        join_length=0,
    )
    category = make_category_attribute("definition")
    ref_a = build_location_reference(loccls, "12", category, None)
    ref_b = build_location_reference(loccls, "13", category, None)
    assert ref_a is not None and ref_b is not None
    assert locref_class_eq(ref_a, ref_b)
    assert not locref_class_lt(ref_a, ref_b)
    assert locref_ordnum_lt(ref_a.ordnums, ref_b.ordnums)
