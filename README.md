# pii-preprocess

This package is intended for the data/document preprocessing stage in the PII
Management flow designed by PIISA.

It will contain:
 * a Python API and command-line entry points to read a number of file formats
   and convert them to PII Source Documents, as defined by [pii-data]
 * Utilities for document transformation (to ease PII processing)
 
 
## Contents

The current contents of the package are:
 * an API for reading CSV files into Tabular source documents
 * a command-line script to convert between CSV files and the YAML canonical
   representation for Source Documents
   
 [pii-data]: https://github.com/piisa/pii-data/

