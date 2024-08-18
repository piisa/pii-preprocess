# pii-preprocess

This package is intended for the data/document preprocessing stage in the PII
Management flow designed by PIISA.

It contains:
 * a Python API and command-line entry points to read a number of file formats
   and convert them to PII Source Documents, as defined by [pii-data]
 * Utilities for document transformation (to ease PII processing)
 
 
## Contents

The current contents of the package are:
 * Internal classes and an API for reading some file types:
     - CSV files (into Table source documents)
	 - [Microsoft Excel] files (into Table source documents)
     - [Microsoft Word] files (into Sequence or Tree source documents)
	 - [Raw text] files (read plain text files into Sequence source documents
	   or, using indentation, into Tree source documents).
 * The capability to read multi-document sources (e.g. local folders) as
   [document collections]
 * A [configurable loader class] thar can load formats by dispatching to
   appropriate subclasses
 * A [plugin infrastructure] that allows to define other document loaders as
   Python packages
 * Some command-line scripts:
    - a generic script that uses the loader class to convert any implemented
	  format to a YAML or plain text file
    - scripts for specific formats:
	   * a script to convert between CSV files and the YAML canonical
         representation for Source Documents
       * a script to convert between plain text files and the YAML
         canonical representation for Source Documents


[pii-data]: https://github.com/piisa/pii-data/
[Microsoft Excel]: doc/msexcel.md
[Microsoft Word]: doc/msword.md
[Raw text]: doc/text.md
[configurable loader class]: doc/loader.md
[plugin infrastructure]: doc/plugin.md
[document collections]: doc/collections.md
