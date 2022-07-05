"""
Simple script to read/write CSV files and convert to/from PII Source documents
"""

from pathlib import Path
import csv
from argparse import ArgumentParser, Namespace


from pii_data.helper.exception import InvArgException
from pii_data.types.localdoc import load_file, TableLocalSrcDocument
from pii_preprocess.doc.csv import LocalCsvDocument


def dump_csv(doc: TableLocalSrcDocument, filename: str, sep: str = None,
             header: bool = None):
    """
    Dump a table SrcDocument to a CSV file
     :param doc: the documento to dump
     :param filename: the output CSV file
     :param sep: the CSV field separator to use
     :param header: add a first row with the column names
    """
    csv_options = {}
    if sep is not None:
        csv_options["delimiter"] = sep

    with open(filename, "w", encoding="utf-8") as f:
        w = csv.writer(f, **csv_options)
        if header:
            columns = doc.metadata.get("column", {}).get("name")
            if columns:
                w.writerow(columns)
        for row in doc.iter_base():
            w.writerow(row['data'])


def to_csv(inputfile: str, outputfile: str, **kwargs):
    """
    Convert a YAML PII Table Source Document to CSV
     :param inputfile: path to the input YAML Source Document
     :param outputfile: path for the output CSV file
    All keyword arguments are passed to the CSV dump function.
    """
    doc = load_file(inputfile)
    if not isinstance(doc, TableLocalSrcDocument):
        raise InvArgException("not a table document: {}", inputfile)
    dump_csv(doc, outputfile, **kwargs)


def from_csv(inputfile: str, outputfile: str, sep: str = None,
             header: bool = None, id_path_prefix: str = None):
    """
    Read a CSV file and convert it to PII Source Document
     :param inputfile: path to the input CSV file
     :param outputfile: path to write the YAML Source Document to
     :param sep: the CSV field separator
     :param header: consider the first row as giving the CSV column names
     :param id_path_prefix: prefix to remove from the input filename when
        building the document id, or `False` to use a random UUID
    """
    csv_options = {}
    if sep:
        csv_options['sep'] = sep
    if id_path_prefix is None:
        id_path_prefix = Path(inputfile).parent
    doc = LocalCsvDocument(inputfile,
                           csv_header=header, csv_options=csv_options,
                           id_path_prefix=id_path_prefix)
    doc.dump(outputfile)


# --------------------------------------------------------------------------

def parse_args():
    args = ArgumentParser(description="Convert CSV files to Table PII Source Doc or viceversa")
    args.add_argument("--noheader", action="store_false",
                      help="no heading row")
    args.add_argument("--sep", help="CSV field separator", metavar="CHAR")
    a = args.add_mutually_exclusive_group()
    a.add_argument("--id-random", action="store_true",
                   help="when reading CSV, assign a random document id")
    a.add_argument("--id-prefix",
                   help="when reading CSV, path prefix to remove from the document id")
    args.add_argument("inputdoc")
    args.add_argument("outputdoc")
    return args.parse_args()


def main(args: Namespace = None):
    if not args:
        args = parse_args()
    if args.inputdoc.endswith((".yml", ".yaml")):
        to_csv(args.inputdoc, args.outputdoc, sep=args.sep,
               header=args.noheader)
    else:
        pfx = False if args.id_random else args.id_prefix
        from_csv(args.inputdoc, args.outputdoc, sep=args.sep,
                 header=args.noheader, id_path_prefix=pfx)


if __name__ == "__main__":
    main()
