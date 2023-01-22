# Plain text documents

Plain text documents are read bu the `TextSrcDocument` dispatcher class. In
addition to standard `SrcDocument` constructor options (e.g. `iter_options`
or`metadata`), the class accepts also a `chunk_options` argument, which
defines the way in which the text file is parsed to split it in chunks.

`chunk_options` is a dictionary of options; the most important of them is the
`mode` option, which defines the main heuristics for the chunking mode. There
are four chunk modes defined: `word`, `line`, `paragraph` and `tree`.


## Word mode

Split by words, where words are chunk of characters separated by non-word
characters (punctuation and whitespace).

The `max_words` option defines the size of each chunk in number or words.


## Line mode

Split by newlines, i.e. each line defines a chunk, with the provision that
blank lines are added to the previous paragraph (hence it does not generate
empty chunks)


## Paragraph

Split by paragraphs, which are identified by using punctuation:
 - by default, paragraphs are delimited by blank lines (lines consisting of
   only whitespace, or empty lines). Any consecutive number of blank lines is
   considered as a single paragraph break
 - optionally, it can also consider the combination of an end of sentence mark
   (period, question or exclamation mark), plus a newline (or a number of
   consecutive newlines).

In addition to this main procedure, additional options can be added to limit
paragraph sizes:
 * "max_words" -- paragraphs longer than max_words are splitted into chunks of
   max words.
 * "min_words" -- paragraphs shorter than min-words are joined to the next one
   (unless this would cause the composite paragraph to be larger than max_words)


## Tree documents

In the special "tree" mode, the code tries to infer a hierarchical tree
document by using leading indent: the "indent" parameter indicates how many
additional indent characters are used to detect each level in the tree, with 0
indent used as top-level elements. Chunks are delimite as in the "line" mode.

Tree documents dumped as raw text by the pii-data package with an indent option
will have this structure, and hence the original tree can be recreated.
