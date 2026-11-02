"""Verify and join the four downloadable model archive parts.

Usage: python scripts/restore_model_bundle.py /folder/containing/parts --extract
"""
import argparse,hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('parts',type=Path);p.add_argument('--extract',action='store_true')
args=p.parse_args();manifest=json.loads((ROOT/'models/archive_manifest.json').read_text())
archive=args.parts/manifest['archive']
with archive.open('wb') as output:
    for part in manifest['parts']:
        path=args.parts/part['name'];digest=hashlib.sha256()
        with path.open('rb') as stream:
            while block:=stream.read(8*1024*1024):digest.update(block);output.write(block)
        if digest.hexdigest()!=part['sha256']:
            raise SystemExit('Checksum mismatch: '+str(path))
if args.extract:
    with tarfile.open(archive) as source:source.extractall(args.parts,filter='data')
    print('Extracted original-layout-base-checkpoint and separated-models.')
    print('Copy separated-models contents into this project\'s models/ directory for the demo.')
else:print(archive)
