
from datetime import datetime
from itertools import islice

from typing import Iterable, Dict


def chunker(it: Iterable[str], size: int, smin: int = 0) -> Iterable[str]:
    """
    Join an iterator into groups of consecutive chunks
     :param it: iterator to group
     :param size: number of items in each group
     :param smin: ignore groups smaller than this size
    """
    it = iter(it)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            return
        if not smin or len(chunk) >= smin:
            yield "".join(chunk)


def add_default_meta(metadata: Dict, origin: str = None, date: str = None):
    """
    Add some default information to the metadata dict, if not already there
    """
    if "document" not in metadata:
        metadata["document"] = {}
    doc = metadata["document"]
    if origin and "origin" not in doc:
        doc["origin"] = origin
    if date and "date" not in doc:
        if not isinstance(date, str):
            date = datetime.utcfromtimestamp(date).isoformat()
        doc["date"] = date


def as_bool(value) -> bool:
    """
    Convert strings or numbers into a boolean
    """
    return str(value).lower() in ('1', 't', 'true', 'yes')
