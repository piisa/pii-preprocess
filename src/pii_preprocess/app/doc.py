"""
Simple script to convert different formats to Source Documents and write them
as YAML or text.
"""

from argparse import ArgumentParser, Namespace

from pii_data.helper.io import base_extension

from ..loader import DocumentLoader


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description="Read documents and convert them to YAML PII Source Doc")
    args.add_argument("inputdoc", help="Input document")
    args.add_argument("outputdoc", help="Output file")

    g0 = args.add_argument_group("Config")
    g0.add_argument("--config", metavar="CONFIG_FILE",
                    help="change the default configuration file that will be loaded")
    g0.add_argument("--config-add", nargs="+", metavar="CONFIG_FILE",
                    help="add additional configuration files")

    g1 = args.add_argument_group("Metadata")
    g1.add_argument("--metadata-document", "--mdoc", metavar="NAME=VAL",
                    nargs="+", help="Add document metadata")
    g1.add_argument("--metadata-dataset", "--mset", metavar="NAME=VAL",
                    nargs="+", help="Add dataset metadata")

    g2 = args.add_argument_group("Output")
    g2.add_argument("--text", action="store_true",
                    help="Save the document as a plain text file")
    g2.add_argument("--indent", type=int, default=0,
                    help="for plain text output, if the document is a tree, represent the tree through indent")
    return args.parse_args()


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    # Create object
    loader = DocumentLoader(args.config)
    if args.config_add:
        for f in args.config_add:
            loader.read_config(f)

    # Prepare metadata
    metadata = {} if args.metadata_document or args.metadata_dataset else None
    if args.metadata_document:
        metadata["document"] = dict(v.split('=', 1) for v in args.metadata_document)
    if args.metadata_dataset:
        metadata["dataset"] = dict(v.split('=', 1) for v in args.metadata_dataset)

    # Read document
    doc = loader.load(args.inputdoc, metadata=metadata)

    # Decide output format
    ext = base_extension(args.outputdoc)
    if args.text:
        format = "text"
    elif not ext:
        format = "yml"
    else:
        format = None

    # Write it
    doc.dump(args.outputdoc, format=format, indent=args.indent)


if __name__ == "__main__":
    main()
