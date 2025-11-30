# Practical Tips

## What LaTeX-package should I use in conjunction with xindy?

We strongly recommend using the LaTeX2e-package `index` written
by David M. Jones, which is available at CTAN. It supports multiple
indexes as well as several shortcuts to easily index terms in a
document. Multiple indexes support the generation of several indexes
for one document. For instance, one can make an author or command
index in addition to a global index.

Another option is to use the `xindy.sty` from Andreas Schlechte
that comes with the **xindy** distribution. Take a look at the
`contrib` directory that should contain a version.

## What editor should I use when writing xindy style files?

Use `Emacs` or `XEmacs`. Turn on the Lisp-mode with

```text
M-x lisp-mode
```

and you can properly indent commands using `M-q`. To enter this
mode automatically add the following lines to the end of the style
file:

```text
^L
;; Local Variables:
;; mode: lisp
;; End:
```

The `^L` (Control-L) can be entered with `C-q C-l`.

## have written a module for processing language *foolandic*. What must I do?

Great! Send it to us! It will become a part of the system in the next
release.
