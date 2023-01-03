# Document loader

The `DocumentLoader` is a configurable loader class thar can load a number
of different document formats by dispatching to appropriate `SrcDocument`
subclasses. It is governed by one or several configuration file(s).

The mechanics of its usage are:
 * instantiate the class
 * optionally add additional configuration files (either in the constructor
   itself or by using the `add_config()` method)
 * call the `load(filename)` method to read and convert a file into a
   [Source Document] object `SrcDcument`
 
 
## Configuration file
 
 A `DocumentLoader` configuration file is a PIISA configuration file that
 contains two fields:
  * `types`: a list of document types to handle. Each type is a dict with
    fields `mime` (document MIME type) and `ext` (file extensions to match; it
    can be a single one or a list of extensions).
  * `loaders`: a dictionary mapping document mime types to document loaders.
    A loader is a dictionary with these fields:
	  - `class`: a Python class to instantiate
	  - `class_kwargs`: keyword arguments to pass to the class constructor
	  
A `DocumentLoader` object loads initially a [default configuration], but more
configurations can be added to it, and those will update (add or overwrite) the
initial configuration.

Note that:
 * The current identification mechanism for file types is just the file
   extension.
 * Files can have an additional compresion extension (i.e. a `.gz`, `.bz2` or
   `.xz` final suffix); this will be taken out before checking the "main"
   extension
 * A given file extension may appear in _more than one_ document type. In this
   case the order is important: they will be tried in the order given in the
   configuration file, and the first one that succeeds (loading a
   `SrcDocument` subclass) is the one returned.


## Adding more loader classes

Additional document types can be added to a `DocumentLoader` object by 
defining an appropriate loader subclass and adding it in a configuration
passed to `add_config()`.

The requirements for such a loader subclass are:
 * It must be a subclass of `SrcDocument` (or one of its subclasses)
 * Its constructor will receive:
     - a positional argument, with the document filename
     - any keyword arguments that can be defined in the `kwargs` configuration
   Any keyword arguments not dealt with in the subclass must be passed to the
   parent class constructor (e.g. `iter_options` or `metadata` argument)


## Conversion script

The `pii-doc` command-line script is a simple script that uses the
`DocumentLoader` class to read any supported file formats and then
converts them to the canonical YAML representation.


[default configuration]: ../src/pii_preprocess/resources/doc-loader.json
[Source Document]: htttps:/github.com/piisa/pii-data/tree/main/doc/srcdocument.md
