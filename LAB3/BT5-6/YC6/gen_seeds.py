#!/usr/bin/env python3
"""Reconstructed generator for the existing Lab 3 AI PDF seeds.

This is a reconstruction made after the original generator was unavailable.
It writes only to an explicitly supplied output directory and never overwrites files.
"""
from __future__ import annotations
import argparse
from pathlib import Path


def stream(dictionary: str, data: bytes) -> bytes:
    return (dictionary + f"/Length {len(data)}\n>>\nstream\n").encode() + data + b"\nendstream"


def pdf(objects: dict[int, bytes], root: int = 1, info: int | None = None) -> bytes:
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: dict[int, int] = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out.extend(f"{number} 0 obj\n".encode())
        out.extend(objects[number])
        out.extend(b"\nendobj\n")
    xref = len(out)
    size = max(objects) + 1
    out.extend(f"xref\n0 {size}\n0000000000 65535 f \n".encode())
    for number in range(1, size):
        if number in offsets:
            out.extend(f"{offsets[number]:010d} 00000 n \n".encode())
        else:
            out.extend(b"0000000000 00000 f \n")
    out.extend(b"trailer\n")
    trailer = f"<<\n/Size {size}\n/Root {root} 0 R\n"
    if info is not None:
        trailer += f"/Info {info} 0 R\n"
    out.extend((trailer + ">>\n").encode())
    out.extend(f"startxref\n{xref}\n%%EOF\n".encode())
    return bytes(out)


def rich_catalog() -> bytes:
    return pdf({
        1: b"<< /Type /Catalog /Pages 2 0 R /Dests 5 0 R /Names 6 0 R /URI 7 0 R /Metadata 8 0 R /StructTreeRoot 9 0 R /Outlines 10 0 R /AcroForm 11 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
        4: b"<< /Title (AI catalog seed) /Author (lab) >>",
        5: b"<< /Dests << /home [3 0 R /Fit] >> >>",
        6: b"<< /Dests << /Names [(home) [3 0 R /Fit]] >> >>",
        7: b"<< /Base (https://example.invalid/) >>",
        8: stream("<<\n/Subtype /XML\n/Type /Metadata\n", b"<x:xmpmeta/>") ,
        9: b"<< /Type /StructTreeRoot /K [] >>",
        10: b"<< /Type /Outlines /Count 0 >>",
        11: b"<< /Fields [] >>",
    }, info=4)


def nested_pages() -> bytes:
    return pdf({
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [5 0 R 4 0 R] /Count 2 /MediaBox [0 0 400 400] /Rotate 90 >>",
        3: b"<< /Title (nested pages) >>",
        4: b"<< /Type /Pages /Kids [7 0 R] /Count 1 /CropBox [0 0 300 300] >>",
        5: b"<< /Type /Page /Parent 2 0 R >>",
        6: b"<< /Type /Page /Parent 4 0 R /Rotate 180 >>",
        7: b"<< /Type /Page /Parent 4 0 R >>",
    }, info=3)


def filtered_metadata() -> bytes:
    xml = b"<meta><title>filtered</title></meta>"
    return pdf({
        1: b"<< /Type /Catalog /Pages 2 0 R /Metadata 5 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
        4: b"<< /Subject (filtered metadata) >>",
        5: stream("<< /Type /Metadata /Subtype /XML /Filter /ASCIIHexDecode ", xml.hex().encode() + b">") ,
    }, info=4)


def incremental_update() -> bytes:
    first = pdf({
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>",
        4: b"<< /Title (first revision) >>",
    }, info=4)
    marker = b"startxref\n"
    old_pos = int(first.rsplit(marker, 1)[1].split(b"\n", 1)[0])
    out = bytearray(first)
    new_object_offset = len(out)
    out.extend(b"5 0 obj\n<< /Title (incremental revision) /Subject (updated) >>\nendobj\n")
    new_xref = len(out)
    out.extend((f"xref\n5 1\n{new_object_offset:010d} 00000 n \ntrailer\n"
                f"<< /Size 6 /Root 1 0 R /Info 5 0 R /Prev {old_pos} >>\n"
                f"startxref\n{new_xref}\n%%EOF\n").encode())
    return bytes(out)


SEEDS = {
    "rich_catalog.pdf": rich_catalog,
    "nested_pages.pdf": nested_pages,
    "filtered_metadata.pdf": filtered_metadata,
    "incremental_update.pdf": incremental_update,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, builder in SEEDS.items():
        path = args.out_dir / name
        if path.exists():
            raise SystemExit(f"refusing to overwrite existing file: {path}")
        data = builder()
        path.write_bytes(data)
        print(f"{path}: {len(data)} bytes")


if __name__ == "__main__":
    main()
