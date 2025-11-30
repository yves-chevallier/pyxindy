# Tutorial

## About xindy

**xindy** means *fle**x**ible **ind**exing s**y**stem*. It can generate
book-like indexes for many document preparation systems (TeX/LaTeX, the
Nroff family, SGML/HTML, etc.). It is configurable and not tied to a
single workflow.

Authors often need an index but find the built-in tools insufficient, so
they use dedicated index processors. **xindy** offers several features
that make it a strong choice:

- **Internationality**: configurable sort/merge rules for many alphabets. Example rule:

    ```text
    (sort-rule "ä" "ae")
    ```

- **User-definable location types**: compose new location classes from
    arabic numbers, roman numerals, letters, and separators (e.g. appendix
    pages like `A-7`, or complex structures such as `Psalm 46:1-8`).

- **Highly configurable markup**: environment-based markup system for
  TeX/LaTeX, SGML/HTML, GNU Info, RTF, Nroff, and more.

