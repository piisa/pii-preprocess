"""
Simple script to convert different formats to Source Documents and write them
as YAML or text.

Can also process document collections.
"""

import sys
from argparse import ArgumentParser, Namespace
from typing.io import TextIO

from typing import Dict, Tuple

from pii_data.helper.io import base_extension, openfile
from pii_data.helper.exception import InvArgException
from pii_data.types.doc import SrcDocument
from pii_data.dump.json import dump_json

from ..loader import DocumentLoader, LoaderWrapper
from ..collection.save import CollectionSaver


JSONL = "jsonl"


def show_info(doc: SrcDocument, out: TextIO = None):
    """
    Print out document metadata
    """
    for s, info in doc.metadata.items():
        print("Section:", s, file=out)
        for k, v in info.items():
            print(f"  {k}: {v}", file=out)


def output_format(args: Namespace, accept: Tuple[str] = None) -> str:
    """
    Decide the output format of the document
    """
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

    if args.verbose:
        print(". Loading:", args.input)

    # Read document
    doc = loader.load(args.input, metadata=metadata)

    # Document information
    if args.doc_info or args.info_only:
        show_info(doc)
        if args.info_only:
            return

    # Decide output format
    format = output_format(args)

    # Write it
    if args.verbose:
        print(". Saving to:", args.output)

    if format == JSONL:
        with openfile(args.output, "at", encoding="utf-8") as f:
            dump_json(doc, f, indent=False)
            print(file=f)
    else:
        doc.dump(args.output, format=format, indent=args.indent)


def process_collection(args: Namespace, metadata: Dict = None):
    """
    Process a document collection (can also process single documents)
    """
    if args.verbose:
        print(". Processing collection:", args.input)

    # Create loader object
    loader = LoaderWrapper(args.config, debug=args.verbose > 1)

    # Open input
    elem = loader.load(args.input, metadata=metadata)

    if args.info_only:
        for doc in elem:
            show_info(doc)
        return

    # Decide output format
    format = output_format(args)

    if args.verbose:
        print(". Saving to:", args.output)

    # Iterate over documents and save them
    with CollectionSaver(args.output, format, indent=args.indent) as svr:
        for doc in elem:
            if args.doc_info:
                show_info(doc)
            svr.save(doc)


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description="Read documents and convert them to PII Source Doc")
    args.add_argument("input", help="Input document")
    args.add_argument("output", help="Output file")

    g0 = args.add_argument_group("Generic")
    g0.add_argument("--verbose", "-v", type=int, metavar="NUM", default=0)
    g0.add_argument("--reraise", action="store_true")

    g0 = args.add_argument_group("Config")
    g0.add_argument("--config", nargs="+", metavar="CONFIG_FILE",
                    help="add additional configuration files")
    g0.add_argument("--collection", action="store_true",
                    help="Treat the source as a document collection")

    g0 = args.add_argument_group("Info")
    g0.add_argument("--doc-info", action="store_true",
                    help="show document metadata")
    g0.add_argument("--info-only", action="store_true",
                    help="Only show information, do not convert document")

    g1 = args.add_argument_group("Metadata")
    g1.add_argument("--metadata-document", "--mdoc", metavar="NAME=VAL",
                    nargs="+", help="Add document metadata")
    g1.add_argument("--metadata-dataset", "--mset", metavar="NAME=VAL",
                    nargs="+", help="Add dataset metadata")

    g2 = args.add_argument_group("Output")
    g2.add_argument("--format", choices=("text", "yml", "json", JSONL),
                    help="Specify output format")
    g2.add_argument("--indent", type=int,
                    help="Output JSON indent, or (if the document is a tree) plain text indent")
    return args.parse_args()


def process(args: Namespace):

    if not args.info_only and not args.output:
        raise Exception("Error: no action specified")

    # Prepare metadata
    metadata = {} if args.metadata_document or args.metadata_dataset else None
    if args.metadata_document:
        metadata["document"] = dict(v.split('=', 1) for v in args.metadata_document)
    if args.metadata_dataset:
        metadata["dataset"] = dict(v.split('=', 1) for v in args.metadata_dataset)

    proc = process_collection if args.collection else process_doc
    proc(args, metadata)


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    try:
        process(args)
    except Exception as e:
        if args.reraise:
            raise
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
