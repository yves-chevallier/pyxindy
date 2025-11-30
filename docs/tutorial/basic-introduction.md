# A Basic Introduction

This section incrementally introduces the most important aspects of
the system. After reading this chapter you should be able to specify
about 80% of the commonly used indexes. The examples are demonstrated
with a TeX markup so one can easily typeset the results **xindy**
produces. You need LaTeX2e and the ISO-Latin enhancements that come
with the `inputenc` package to run the following examples. Also the
**xindy** system must already be installed.

## Running xindy

Create a new directory somewhere and copy some files from the
distribution directory `Doc/tutorial/` by typing

```bash
$ mkdir tutorial
$ cd tutorial
$ cp <distrib-dir>/Doc/tutorial/*.raw .
$ cp <distrib-dir>/Doc/tutorial/*.tex .
```

with `distrib-dir` replaced by the actual location. Now create a
file `style1.xdy` with the following content:

```text
;; This is a first example using `xindy'.

(define-location-class "page-numbers" ("arabic-numbers"))
(define-attributes (("definition" "usage")))

```

Now run **xindy** by typing (the switch ``-l`' is the lowercase
letter `L')

```bash
$ xindy -l ex1.xlg style1.xdy ex1.raw
```

You should see something like

```text
This is `xindy' version 1.1 January 1997 (some-arch).

Opening logfile "ex1.xlg" (done)
Reading indexstyle...
Loading module "style1.xdy"...
Finished loading module "style1.xdy".
Finished reading indexstyle.
Finalizing indexstyle... (done)

Reading raw-index "ex1.raw"...
Finished reading raw-index.

Processing index... [10%] [20%] [30%] [40%] [50%] [60%] [70%] [80%] [90%] [100%]
Finished processing index.

Writing markup... [10%] [20%] [30%] [40%] [50%] [60%] [70%] [80%] [90%] [100%]
Markup written into file "ex1.ind".

```

**xindy** has now successfully compiled the index `ex1.raw` using
your index style `style1.xdy`. The result is now stored in file
`ex1.ind`. You can view this file but currently it only contains an
unreadable mix of data.

But now let's come back to our index style. The syntax of the command
is in a Lisp-like form with lots of braces, looking a little bit
weird, but you'll soon get used to it. What is the meaning of the two
commands we specified? The first command informed **xindy** that we
like to process page numbers. We do this by defining a new
*location class* named `page-numbers`. The page numbers consist
of `arabic-numbers` as we might expect but this is not necessarily
true---imagine your page numbers consisted of roman numerals instead.
When reading the *raw index* contained in file `ex1.raw`
**xindy** checks all locations if they match all known location
classes. Since in our example the only known location class is the
class of page numbers which are written using arabic digits, all
locations will be checked if they are correct page numbers.

The second command tells **xindy** that we use two types of
attributes for location references. Most often the locations in an
index denote different meanings. For example, in mathematical texts
one will distinguish the *definition* of a mathematical term from
its *usage*. Sometimes these are typeset using different font
shapes such as *italic* or font series such as **boldface**. Each
location has an associated attribute which, if it is unspecified,
defaults to the attribute `default`. With this command you have
made these attributes known to the system, which makes it possible to
assign different markup to these attributes later on.

## Adding some Markup

Until now you haven't seen something exciting, so its time to specify
some markup. Add the following lines to our index style:

```text
(markup-index :open  "~n\begin{theindex}~n"
              :close "~n\end{theindex}~n"
              :tree)

(markup-locref :class "page-numbers" :attr "definition"
               :open  "{\bf " :close "}")

(markup-locclass-list :open "\quad{}")
(markup-locref-list :sep ", ")

```

Now run **xindy** again and afterwards LaTeX:

```bash
$ xindy -l ex1.xlg style1.xdy ex1.raw
$ latex ex1.tex
```

You can view `ex1.dvi` with your prefered viewer (maybe `xdvi`
or something else) to get a first impression of your results. Maybe
your are not satisfied (for sure you aren't), because it still looks
very confusing. What did the above rules tell **xindy**? When you
view the file `ex1.ind` which is the result **xindy** generates,
you'll recognize some of the *markup tags* you specified. The
following is an excerpt of this file:

```latex
\begin{theindex}
  academia\quad{}{\bf 1}acafetado\quad{}{\bf 2}acalmar\quad{}{\bf 4}
  açafrão\quad{}{\bf 3}indexflat\quad{}1hierarchical\quad{}2
  veryhierarchical\quad{}3impressive\quad{}4saber\quad{}{\bf 7}
  sabor\quad{}{\bf 8}sabão\quad{}{\bf 6}sábado\quad{}{\bf 5}
\end{theindex}
```

First of all you'll see that the file starts with the string
`\begin{theindex}`
 and ends with
`\end{theindex}`
.
Additionally some locations are correctly enclosed into a TeX macro
that typesets them in shape boldface, whereas others aren't. The
boldface ones are all those locations from the raw index that have the
attribute `definition`.

The `:open` and `:close` keyword arguments each take a string as
argument. The first one is written to the file when *opening* an
enviroment, whereas the latter one *closes* an environment. What we
have specified is the markup for the whole index (which is actually
printed only once) and the markup for all locations of class
`page-numbers` which own the attribute `definition`. Here we
have cleanly separated the structured markup from the visual one,
allowing an easy redefinition if we decide, for example, to markup the
`definition`-locations in italics instead of boldface.

Some words on *keyword arguments* and *switches*. Keyword
arguments such as `:open` or `:close` always take exactly one
argument which must be positioned right after the keyword separated by
a whitespace (a blank or a tab-stop). Switches don't take any
arguments. For example, `:tree` in the command `markup-index` is
a switch and thus it does not take an argument. We will use this
terminology throughout the rest of this document.

The third command caused **xindy** to insert a horizontal space
between the keyword and the locations (the TeX command
`\quad{}`
 simply inserts a specific horizontal space). The last
command caused **xindy** to separate all location references from
each other with a comma followed by a blank, independently of any
location class.

As you already may have observed, the tilde sign `~` serves as
a *quoting character*.

We continue specifying markup to get a printable result by adding more
markup:

```text
(markup-indexentry :open "~n  \item "           :depth 0)
(markup-indexentry :open "~n    \subitem "      :depth 1)
(markup-indexentry :open "~n      \subsubitem " :depth 2)
```

This assigns different markup for the different hierarchy layers of
the indexentries. Our index is hierarchically organized. It contains
items which themselves contain more sub-items which also might contain
sub-sub-items. Each layer is started by a different markup which is
correctly assigned with the `:depth` keyword argument. The layers
are numbered by their *depth* starting from zero.

Now run **xindy** and TeX again and enjoy your first index. It's
easy, isn't it! The output `ex1.ind` looks like the following:

```latex
\begin{theindex}

  \item academia\quad{}{\bf 1}
  \item acafetado\quad{}{\bf 2}
  \item acalmar\quad{}{\bf 4}
  \item açafrão\quad{}{\bf 3}
  \item index
    \subitem flat\quad{}1
    \subitem hierarchical\quad{}2
    \subitem very
      \subsubitem hierarchical\quad{}3
      \subsubitem impressive\quad{}4
  \item saber\quad{}{\bf 7}
  \item sabor\quad{}{\bf 8}
  \item sabão\quad{}{\bf 6}
  \item sábado\quad{}{\bf 5}

\end{theindex}
```

Hmm, as you might have seen there are several problems that need
further investigation. The index contains some Portuguese words that
are printed correctly but should appear at other positions inside the
index. For instance, the word *sábado* should appear before the
word *saber* since *á* must be sorted as if it were simply an
*a*. The reason why these words are not sorted correctly is
simple---the accentuated letters have codes beyond position 128 in the
ISO-Latin alphabet. Sorting based on these codes yields this incorrect
order.

What to do? We can define for each of the words containing these
special characters an explicit *print key*. The print key describes
the printed representation of the keyword whereas the *key* or
*main key* is used for sorting and merging. A very tedious task
which is not a very clever solution since in a non-english language
many many words contain these special cases. We follow the way
**xindy** offers: *keyword-mappings*.

## Keyword Mappings

What are keyword mappings for? A good question. I'll try to give some
answers.

* *Merging of differently written words*. Some text formatting
systems allow different writings for the same word. For example, TeX
can be used with ISO-Latin characters as well as with its own
character sequences. If a document is composed from smaller ones
possibly written by different authors using different forms of writing
the index entries, the same terms may happen to be written differently
and consequently we need a mechanism to identify them as equal.
* *Specifying the sort order*. As outlined in the previous
section it is really difficult and error-prone to specify the sort key
for each keyword explicitly. Sometimes the sort order is even
different for the type of the document, as it happens in German, where
two different types of sortings exist, one for everyday indexes and
one for dictionaries. The sort order actually defines the position of
arbitrary language-specific letters inside of an index.

A detailed elaboration of these ideas can be found in the paper *An
International Version of MakeIndex* by Joachim Schrod [3].
It describes the ideas that led to modifications on one of the
ancestors of the **xindy** system: `makeindex` [4].

The keyword mappings are as follows. The *merge key* is generated
from the *main key* with the so called *merge mapping*. The
merge mapping can be specified with the command `merge-rule`. The
*sort key* is derived from the merge key using the *sort
mapping* specified with the `sort-rule` command. The following
scheme shows this mapping process:

![](../assets/mapping.svg)

We will use this command now to define a suitable sort mapping that
fits our needs:

```
(sort-rule "à" "a")
(sort-rule "á" "a")
(sort-rule "ã" "a")
(sort-rule "è" "e")
(sort-rule "é" "e")
(sort-rule "ç" "c")
```

These rules define mappings from a keyword to a *normalized*
version. In the logfile `ex1.xlg` these transformations are logged so
that one can see how these mappings are performed. In this example we
do not need any `merge-rule` but we will see applications in
further examples.

Running **xindy** and TeXing the result now places the indexentries
at the right positions.

The result is now quite satisfying if the index entries weren't
clumped together that much. We usually want the different index
entries beginning with the same letter be optically separated from the
ofhers. This improves readability and there must be a way to
accomplish this---the *letter groups*.

## Letter Groups

To group indexentries we must define what indexentries form a group.
The clustering is done by matching the keywords' prefixes (taken from
the *sort key*) with a user-defined table of prefixes and define
appropriate markup that separates the groups from each other. Here it
goes.

```text
(define-letter-groups
  ("a" "b" "c" "d" "e" "f" "g" "h" "i" "j" "k" "l" "m"
   "n" "o" "p" "q" "r" "s" "t" "u" "v" "w" "x" "y" "z"))

(markup-letter-group-list :sep "~n\indexspace")
```

This defines the given list of letter groups. When forming the letter
groups, each letter group is checked if it matches a prefix of the
indexentries' sort key. The longest match assigns the index entry to
this letter group. If no match was possible the index entry is put into
group `default`.

The result now looks much better than before. You have now learned the
basic features that you need to specify everyday indexes. In the next
chapter we'll continue to make you an expert in indexing.
