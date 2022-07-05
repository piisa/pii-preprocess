# pii-preprocess

This package is intended for the data/document preprocessing stage in the PII
Management flow designed by PIISA.

It will contain:
 * a Python API and command-line entry points to read a number of file formats
   and convert them to PII Source Documents, as defined by [pii-data]
 * Utilities for document transformation (to ease PII processing)
 
 
## Contents

The current contents of the package are:
 * Classes and an API for reading some file types:
     - CSV files (into Table source documents)
     - [Microsoft Word] files (into Sequence or Tree source documents)
	 - [Raw text] files (read plain text files into Sequence source documents
	   or, using indentation, into Tree source documents).
 * A [configurable loader class] thar can load formats by dispatching to
   appropriate subclasses
 * Some command-line scripts:
    - a generic script that uses the loader class to convert any implemented
	  format to a YAML or plain text file
    - scripts for specific formats:
	   * a script to convert between CSV files and the YAML canonical
         representation for Source Documents
       * a script to convert between plain text files and the YAML
         canonical representation for Source Documents


[pii-data]: https://github.com/piisa/pii-data/
[Microsoft Word]: doc/msword.md
[Raw text]: doc/plain-text.md
[configurable loader class]: doc/loader.md

