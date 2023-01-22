"""
Simple script to read & write Source Documents in either YAML or raw text
formats
"""

from argparse import ArgumentParser, Namespace

from pii_data.helper.io import base_extension
from pii_data.types.localdoc import LocalSrcDocumentFile

from ..doc.text import TextSrcDocument, CHUNK_MODES


def from_plain(inputfile: str, args: Namespace) -> TextSrcDocument:
    """
    Read a plain text file
    """
    opt = {"mode": args.mode}
    if args.input_indent:
        opt["indent"] = args.input_indent
    if args.chunk_options:
        opt.update(v.split("=", 1) for v in args.chunk_options)
    return TextSrcDocument(inputfile, chunk_options=opt)


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description='Convert from YAML PII Source Doc to plain raw text or viceversa')
    args.add_argument('inputdoc', help='input file (text or YAML)')
    args.add_argument('outputdoc',
                      help='output file (format to be deduced from file extension)')
    args.add_argument('--mode', choices=CHUNK_MODES, default="line",
                      help="text chunking mode (default: %(default)s)")
    args.add_argument('--chunk-options', metavar="NAME=VAL", nargs="+",
                      help="text chunking options")
    args.add_argument('--input-indent', type=int, default=0, metavar="NUMCHARS",
                      help="indent value to detect tree hierarchy in text input")
    args.add_argument('--output-indent', type=int, default=None,
                      metavar="NUMCHARS",
                      help="output indent value (for text or json output)")
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
    doc.dump(args.outputdoc, indent=args.output_indent)


if __name__ == '__main__':
    main()
