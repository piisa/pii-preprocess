# Microsoft Word documents

The msword classes read `docx` documents into PII Source Documents, by using
the `MsWordDocument` class, and split the document into paragraphs (by
newlines); each paragraph creates one document chunk.

`MsWordDocument` is a wrapper class that will actually deliver two different
flavors:
 - a `SequenceMsWordDocument`, whose struct and full iterations yield a
   linear sequence of paragraphs
 - a `TreeMsWordDocument`, which uses Word Heading styles to build a tree of
   paragraphs, and its struct iteration yields a sequence of subtrees (each one
   being either a top-level section with all its subsections, or an isolated
   paragraph).
   The full iteration of a `TreeMsWordDocument` flattens the structure and
   delivers the same chunks as if the document had been opened as a
   `SequenceMsWordDocument` (though the chunk ids will be different).


## Newlines and blank paragraphs

All paragraphs produced on an iteration end with a newline.

When parsing, paragraphs consisting only of whitespace (spaces, tabs,
newlines) are joined with the previous paragraphs (therefore a given chunk
might end with _more than one newline_, if there were blank lines in the
document).

## Document metadata

Some document-level metadata, if present in the file, is added to the document
header: title, author & category.
