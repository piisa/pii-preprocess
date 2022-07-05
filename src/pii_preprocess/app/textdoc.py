"""
Simple script to read & write Source Documents in either YAML or raw text
formats
"""

from argparse import ArgumentParser, Namespace

from pii_data.helper.io import base_extension
from pii_data.types.localdoc import LocalSrcDocumentFile
from pii_data.doc import dump_text

from ..doc.text import TextSrcDocument


def from_plain(inputfile: str, args: Namespace) -> TextSrcDocument:
    """
    Read a plain text file
    """
    opt = {"mode": args.mode}
    if args.indent:
        opt["indent"] = args.indent
    if args.chunk_options:
        opt.update(v.split("=", 1) for v in args.chunk_options)
    return TextSrcDocument(inputfile, chunk_options=opt)


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description='Convert from YAML PII Source Doc to plain raw text or viceversa')
    args.add_argument('inputdoc')
    args.add_argument('outputdoc')
    args.add_argument('--indent', type=int, default=0, metavar="NUMCHARS",
                      help="indent value to detect/generate tree hierarchy")
    args.add_argument('--mode', choices=("line", "tree", "paragraph", "word"),
                      default="line",
                      help="text chunking mode (default: %(default)s)")
    args.add_argument('--chunk-options', metavar="NAME=VAL", nargs="+",
                      help="text chunking options")
    return args.parse_args()


def main(args: Namespace = None):

    if not args:
        args = parse_args()

    # Read document
    ext1 = base_extension(args.inputdoc)
    if ext1 in ('.yml', '.yaml'):
        doc = LocalSrcDocumentFile(args.inputdoc)
    else:
        doc = from_plain(args.inputdoc, args)

    # Write it
    ext2 = base_extension(args.outputdoc)
    if ext2 in ('.yml', '.yaml'):
        doc.dump(args.outputdoc)
    else:
        dump_text(doc, args.outputdoc, args.indent)


if __name__ == '__main__':
    main()
