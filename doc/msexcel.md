# Microsoft Excel documents

The msexcel classes read `xlsx` documents into PII Source Documents, by using
the `TableExcelDocument` class, and split the document into cells. Only the
first sheet is read, so far.


## Metadata

### Document metadata

Some document-level metadata, if present in the Excel file, is added to the
document header: _title_, _author_ (aka _creator_), _subject_ & _modified_.

If the `header` argument to the class constructor is `True` (which is the
default), the first row is assumed to contain column names; they will also be
added as document metadata.


### Cell metadata

Each document chunk will contain:
 * `id`: an identifier for the chunk, using standard spreadsheet conventions,
   i.e. `<column><row>`, where `<column>` is alphabetical and `<row>` is
   numerical
 * `data`: the cell textual content
 * `context`: a dictionary with two elements: `row` (row number, starting at 1)
   and `column` (column number, also starting at 1, and, if available, column
   name)


## Iteration

Document iteration follows the standard rules for Table Source Documents:
 * the base iteration produces cells as DocumentChunk objects, in row major order
 * structured iteration produces rows, which can then be uterated to produce
   columns
   
### Iteration with context

When iterating with context, if column names are availabale, the cell context
will automatically be augmented with a `before` field that will contain the
column name plus a colon plus a space.
