# Features

Here is a brief description of the most important features of xindy:

## Internationalization

xindy can be configured to process indexes for many languages with different letter sets and different sorting rules. This captures also different orders (collating sequences such as Ly, Ny in Hungarian, or Ch, Ll in Spanish), even within one language. For example, many roman languages such as Italian, French, Portuguese or Spanish contain accented letters such as À, Â, ñ;. Other languages from northern Europe have additional letters like Ä, Ø, æ or ß; which often can't be processed by many index processors, let alone sorting them correctly into an index.

The xindy-system can be configured to process these alphabets with language-specific rules. One very basic example of such a rule would be (sort-rule "ä" "ae") defining that a word containing the umlaut-a will be sorted as if it contained the letters ae instead. This is one of the two forms of how the umlaut-a is sorted into german indexes. With an appropriate set of rules one can express the complete rules of a specific language.

## Mark-up Normalization

Formatters usually add mark-up to the raw index data. Often different encodings are used for the representation of an otherwise equal thing (e.g., in the context of TeX, umlaut-a may be represented as ä, as ^^e4, or as \"a). xindy offers means to normalize these different encodings into one internal encoding, which is especially useful if the raw index stems from several different sources.

## Manage Non-Standard Locations

Index entries refer to locations, commonly used locations are page numbers, section numbers, etc. xindy allows new types of locations to be defined. An example structure is represented by the following locations: Exodus 7:4, Psalm 46:1-8, and Genesis 1:31. The structure of bible verses can be described in xindy, allowing to correctly sort and process indexes for documents with such a strucure. Here the Psalms would be sorted before the Genesis verses in contrast to the usual order based on the lexicographic order of the chapter names.

## Module Support

All definitions concening the processing and tagging of an index are specified in a so-called index style. To support maximum reuse of building blocks xindy implements support for index style modules that allow end-users to profit from already existing styles. Just thing of modules as of LaTeX-packages that are used to load new features and definitions into the core system.

## Highly Configurable Mark-Up

Since an index processor is only one component in a document preparation system it ought to fit smoothly into the rest of the environment. Many document preparation systems use the concept of hierarchical environments that can be used to describe the mark-up of the text entities. Our approach is based on this concept which has proven to be expressive enough for almost any applications. Systems such as SGML (and its instance HTML), XML, GNU Info use environments a the underlying mark-up concept. The mark-up of an index can be defined for all of these and various other systems such as TeX/LaTeX, nroff, etc. in a very comfortable though extremly powerful way xindy comes with a context-based mark-up strategy that uses a form of event dispatching mechanism (sounds cool, eh? It is!)
