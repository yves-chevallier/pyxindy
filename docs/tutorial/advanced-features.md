# Advanced Features

In the following sections you'll learn more about the features of
**xindy**. We'll show you how you can define your own
location classes, specify the letter groups in more detail and bring
you close to more specfic markup features. After reading this chapter
you should be able to master about 95% of the commonly used indexes.

## Location Classes

We continue using a more complex index. Copy the current style to a
new file (now `style2.xdy`) and run **xindy** on the raw index
`ex2.raw` by typing:

```bash
$ cp style1.xdy style2.xdy
$ xindy -l ex2.xlg style2.xdy ex2.raw
```

You should see some error messages indicating that something is
unknown to **xindy**. What has happend? The messages should be
similar to the following snapshot:

```text
 ...
WARNING:
location-reference "B-5" did not match any location-class! (ignored)
WARNING:
location-reference "C-8" did not match any location-class! (ignored)
WARNING:
location-reference "iv" did not match any location-class! (ignored)
WARNING:
location-reference "ii" did not match any location-class! (ignored)
 ...
```

The index contains new, and therefore unknown, location classes. The
first one has an appendix-like style, whereas the second one seems to
be lowercase roman numerals. **xindy** reported, that it doesn't know
these locations and therefore knows nothing about their internal
structure. We make them known to the system by adding the following
commands to the style file.

```text
(define-location-class "roman-pages" ("roman-numerals-lowercase"))
(define-location-class "appendices" ("ALPHA" :sep "-" "arabic-numbers"))
(define-location-class-order ("roman-pages" "appendices"))
```

The first command tells **xindy** that there exist some page numbers
that are written with roman lowercase letters. The second one defines
the structure of the appendix locations. They consist of three
elements, a capital letter, a separator---which is a hyphen in our
case---and finally an arabic number. To be able to correctly
distinguish separator strings from the names of the known
*basetypes*, the argument `:sep` indicates, that the following
is a separator. The last command simply says that the locations which
are roman numerals shall appear before the appendix locations. So far
we know three different basetypes. The built-in basetypes of
**xindy** are:

- `arabic-numbers`: all non-negative numbers beginning with zero (0,
  1, 2, ...).
- `roman-numerals-uppercase`, `roman-numerals-lowercase`: roman
  numerals I, II, III, (IIII/IV), V, ... (old and new systems), with
  uppercase and lowercase variants.
- `ALPHA`, `alpha`: US-ASCII alphabet letters (uppercase and lowercase).
- `digits`: the digits 0–9 in order.

`Fine,', you'll say, `but what if my basetypes are completely
different?' You're right! But **xindy** offers you to define your own
alphabets. For example, you can define a new alphabet by writing

```text
(define-alphabet "my-personal-alphabet" ("Hi" "ho" "here" "I" "go"))
```

This is a valid alphabet that consists of 5 *letters*. You can now
define a location class

```text
(define-location-class "my-personal-class"
    ("my-personal-alphabet" :sep "-" "arabic-numbers"))
```

to match all of the following locations: *Hi-12, ho-2, here-709,
I-9, go-42*. **xindy** will recognize them and be able to sort them
according to your specification which says that *Hi* comes before
all others and *here* is exactly at the third position. So they
will be sorted lexicographically, layer by layer, until it can decide
which one is before or after the other. We have prepared a concrete
example. Do you remember the example we gave when we spoke about
indexing bible verses? This exactly matches the situation of such a
self-defined alphabet which could look like the following definitions:

```text
(define-alphabet "bible-chapters"
    ("Genesis" "Exodus" "Leviticus" "Numbers" "Deuteronomy"
     ... ))
(define-location-class "bible-verses"
    ("bible-chapters" :sep " " "arabic-numbers" :sep "," "arabic-numbers"))
```

This description would match locations like *Genesis 1,3*,
*Exodus 7,8*, etc.

Now run LaTeX on `ex2.tex` and view the results. It looks a
little bit strange since **xindy** has automatically built ranges of
successive locations. The first locations of the index entry *roman*
actually denote the range *ii* until *iv*. *Ranges* consist
of location references. To typeset them correctly you can specify

```text
(markup-range :sep "--")
```

This indicates that location reference forming a range shall be
separated by a hyphen. Running **xindy** and LaTeX again gives a
better idea of how it should look like. Here is a part of the
generated output.

```text
  ...
\item appendices\quad{}A-1, A-7, A-11, B-3--B-5, C-1, C-8, C-12,
         C-13, C-22, D-2, D-3, D-5, D-10
  ...
```

## Hierarchical Location Classes

Somehow a lot of space is wasted when looking at the first index entry.
Modify the definition of the location class for appendices as follows
and add the other commands as well:

```text
(define-location-class "appendices"
                       ("ALPHA" :sep "-" "arabic-numbers")
                       :hierdepth 2)
(markup-locref-list            :sep "; " :depth 0 :class "appendices")
(markup-locref-list :open "~~" :sep ", " :depth 1 :class "appendices")
```

*Note: Since the tilde character serves as our quoting character it
must be quoted itself in the above example.* Run **xindy** and view
the output stored in `ex2.ind`. The output looks similar to the
following:

```text
 ...
\item appendices\quad{}A~1, 7, 11; B~3--5; C~1, 8, 12, 13, 22;
         D~2, 3, 5, 10
 ...
```

You can see that the location references of this class have been
transformed into a hierarchical structure caused by the
`:hierdepth` argument. Additionally we have specified markup for
the layers of this class separately for the depths 0 and 1. The
locations at depth 0 are separated by a `;' whereas the ones at depth
1 are separated by a `,'.

Maybe you get an impression why we named **xindy** a *flexible*
system.

## More about Letter Groups

More problems arise when using languages with different letter
schemes. Hungarian is an example. In Hungarian indexes the words
beginning with the letters *Cs, Ly, Ny* and more are printed in a
separate block. The words beginning with *Ly*, for example, appear
behind the words beginning with an *L*. **xindy** allows to define
this kind of letter groups as well. Add the following lines to the
style file.

```text
(define-letter-group "ly" :after "l" :before "m")
(define-letter-group "ny" :after "n" :before "o")

(markup-letter-group :open-head "~n {\bf " :close-head "}"
                     :capitalize)
```

The result looks like the following:

```text
...
{\bf Ly}
\item lyuk\quad{}1
\item lyukas\quad{}2

\indexspace

{\bf M}
\item maga\quad{}1
\item magyar\quad{}2

\indexspace

{\bf N}
\item nagy\quad{}1
\item nagyon\quad{}9
\item nègy\quad{}4

\indexspace

{\bf Ny}
\item nyelv\quad{}1
\item nyolc\quad{}8
 ...
```

The result describes what the purpose of the above commands is. It
becomes prettier from step to step, doesn't it?

You have now learned most of the features of **xindy**. Go playing
around a little bit. For a detailed description of all commands and
all their arguments and switches you should reference the manual that
comes with this distribution.
