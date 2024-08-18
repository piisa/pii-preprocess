# Document collections

A document collection is an object that, when iterated, produces Source
Document objects.

There can be different sources of collections; the current implementation
contains three of them: a folder, a JSON-L file and a ZIP file.

The root class to manage collections is the `DocumentCollection` class. Those
three variants are subclasses of this one.

A `DocumentCollection` class can be iterated; each iteration produces a
`SrcDocument` object.

A companion class, `CollectionSaver`, can be used to save a bunch of
`SrcDocuments`.


## Folder document collections

This variant is created by the `FolderDocumentCollection` class can read all
the documents in a folder. It also accepts arguments to apply a globbing
pattern to select only some of the documents in the folder, and to recurse
into subfolders.


## NDJSON document collections

This variant can read a [JSON-L] aka NDJSON files (a file containing one JSON
document per line). Each document must still be a valid PIISA serialized file.


## Zipfile document collections

This variant can read all the documents packaged inside a ZIP file 


[JSON-L]: https://jsonlines.org
