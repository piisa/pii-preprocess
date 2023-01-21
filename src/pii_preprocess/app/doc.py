"""
Simple script to convert different formats to Source Documents and write them
as YAML or text.

Can also process document collections.
"""

from argparse import ArgumentParser, Namespace

from typing import Dict, Tuple

from pii_data.helper.io import base_extension
from pii_data.helper.exception import InvArgException

from ..loader import DocumentLoader, LoaderWrapper
from ..collection.save import CollectionSaver


def output_format(args: Namespace, accept: Tuple[str] = None) -> str:
    if args.format:
        return args.format
    ext = base_extension(args.output)
    if not ext:
        raise InvArgException("unknown output format")
    ext = ext[1:]
    if accept and ext not in accept:
        raise InvArgException("invalid output format: {}", ext)
    return ext


def process_doc(args: Namespace, metadata: Dict = None):
    """
    Process a document
    """
    # Create object
    loader = DocumentLoader(args.config)

    # Read document
    doc = loader.load(args.input, metadata=metadata)

    # Decide output format
    format = output_format(args)
    if format == "ndjson":
        raise InvArgException("ndjson not valid for individual documents")

    # Write it
    doc.dump(args.output, format=format, indent=args.indent)


def process_collection(args: Namespace, metadata: Dict = None):
    """
    Process a document collection (can also process single documents)
    """
    # Create loader object
    loader = LoaderWrapper(args.config)

    # Open input
    elem = loader.load(args.input, metadata=metadata)

    # Decide output format
    format = output_format(args)

    # Iterate over documents and save them
    with CollectionSaver(args.output, format, indent=args.indent) as svr:
        for doc in elem:
            svr.save(doc)


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description="Read documents and convert them to YAML PII Source Doc")
    args.add_argument("input", help="Input document")
    args.add_argument("output", help="Output file")

    g0 = args.add_argument_group("Config")
    g0.add_argument("--config", nargs="+", metavar="CONFIG_FILE",
                    help="add additional configuration files")
    g0.add_argument("--collection", action="store_true",
                    help="Treat the source as a document collection")

    g1 = args.add_argument_group("Metadata")
    g1.add_argument("--metadata-document", "--mdoc", metavar="NAME=VAL",
                    nargs="+", help="Add document metadata")
    g1.add_argument("--metadata-dataset", "--mset", metavar="NAME=VAL",
                    nargs="+", help="Add dataset metadata")

    g2 = args.add_argument_group("Output")
    g2.add_argument("--format", choices=("text", "yml", "json", "ndjson"),
                    help="Specify outout format")
    g2.add_argument("--indent", type=int,
                    help="JSON indent, or (if the document is a tree) plain text indent")
    return args.parse_args()


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    # Prepare metadata
    metadata = {} if args.metadata_document or args.metadata_dataset else None
    if args.metadata_document:
        metadata["document"] = dict(v.split('=', 1) for v in args.metadata_document)
    if args.metadata_dataset:
        metadata["dataset"] = dict(v.split('=', 1) for v in args.metadata_dataset)

    # Prepare metadata
    metadata = {} if args.metadata_document or args.metadata_dataset else None
    if args.metadata_document:
        metadata["document"] = dict(v.split('=', 1) for v in args.metadata_document)
    if args.metadata_dataset:
        metadata["dataset"] = dict(v.split('=', 1) for v in args.metadata_dataset)

    proc = process_collection if args.collection else process_doc
    proc(args, metadata)


if __name__ == "__main__":
    main()
