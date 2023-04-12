#!/usr/bin/env python3

import argparse
import gzip
import mmap

from elftools.elf.elffile import ELFFile

KEY_START_BYTES = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff"
KEY_LEN = 56


def extract(binary, *, decompress=True):
    with open(binary, "rb") as f:
        elf = ELFFile(f)
        s = elf.get_section_by_name(".noptrdata")
        stream = s.stream
        with mmap.mmap(stream.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            api_key_start = mmap_obj.find(KEY_START_BYTES)
            mmap_obj.seek(api_key_start)
            api_key = mmap_obj.read(56)
            spid_start = mmap_obj.find(KEY_START_BYTES, api_key_start + 56)
            mmap_obj.seek(spid_start)
            spid = mmap_obj.read(KEY_LEN)

    if decompress:
        api_key = _decompress(api_key)
        spid = _decompress(spid)

    return api_key, spid


def _decompress(key):
    return gzip.decompress(key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary")
    args = parser.parse_args()

    api_key, spid = extract(args.binary)
    print(f"API KEY: \t{api_key.decode()}")  # noqa: T201
    print(f"SPID: \t\t{spid.decode()}")  # noqa: T201