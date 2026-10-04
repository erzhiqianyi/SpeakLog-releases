#!/usr/bin/env python3
"""Copy only allowlisted public files into a new or empty deployment directory."""
import argparse
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from validate_website import is_public_file


def build(source, output):
    if Path(source).is_symlink() or Path(output).is_symlink():
        raise ValueError("Source and output directory must not be symlinks")
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_dir():
        raise ValueError(f"Source directory does not exist: {source}")
    if output == source or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError("Output must not overlap the source website")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Output must be a new or empty directory; existing files are never deleted")
    files = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"Symlinks are not allowed in the source website: {relative}")
        if path.is_file() and is_public_file(relative):
            files.append((path, relative))
    output.mkdir(parents=True, exist_ok=True)
    for path, relative in files:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    return [relative.as_posix() for _, relative in files]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "website")
    args = parser.parse_args()
    try:
        files = build(args.source, args.output)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Build refused: {exc}\n")
    print(f"Built {len(files)} public files into {args.output}")
    for file in files:
        print(f"  {file}")


if __name__ == "__main__":
    main()
