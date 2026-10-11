#!/usr/bin/env python3
"""ReSkate PS5 experimental installer. Python 3.11+, standard library only.

Copyright (c) 2026 ReSkate PS5 contributors. SPDX-License-Identifier: MIT
Default mode verifies local inputs and prints a plan. --install writes to PS5.
"""
import argparse
import contextlib
import ftplib
import hashlib
import io
import ipaddress
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
TITLE = '/data/homebrew/PPSA99223'
ROOT = '/data/reskate'
GAME = ROOT + '/prefix/dosdevices/c:/Games/ReSkate/'
CACHE = ROOT + '/prefix/dosdevices/c:/users/wowps5/AppData/Local/ReSkate/cache/25414733/'
BASE_SHA = 'c09926955428d67b5a90db7f16fde5a162b6057d388d8579365a38123d1e7df9'
MARKER = b'ReSkate-PS5 experimental installer v1\n'
BLOCK = 128 * 1024


def digest(stream):
    result = hashlib.sha256()
    while chunk := stream.read(BLOCK):
        result.update(chunk)
    return result.hexdigest()


def relative(name):
    if (not isinstance(name, str) or not name or '\\' in name or ':' in name
            or any(ord(c) < 32 for c in name) or name.startswith('/')
            or any(p in ('', '.', '..') for p in name.split('/'))):
        raise ValueError('Unsafe relative path')
    return name


def local_file(root, name):
    relative(name)
    root = root.resolve(strict=True)
    path = root / name
    # Reject symlinks/junctions even if they lead back into the input tree.
    current = path
    while current != root:
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('Linked input path: ' + name)
        current = current.parent
    if not path.resolve(strict=True).is_relative_to(root) or not path.is_file():
        raise ValueError('Input escaped its directory: ' + name)
    return path


def confined(remote):
    if (not remote.startswith((ROOT + '/', TITLE + '/')) or '\\' in remote
            or any(ord(c) < 32 for c in remote) or '..' in remote.split('/')
            or '.' in remote.split('/') or '//' in remote):
        raise ValueError('Unsafe remote path')
    return remote


def manifest(name):
    data = json.loads((HERE / 'manifests' / name).read_text(encoding='utf-8'))
    seen = set()
    for item in data:
        relative(item['path'])
        if item['path'].casefold() in seen:
            raise ValueError('Duplicate manifest path')
        seen.add(item['path'].casefold())
        if not re.fullmatch('[0-9a-f]{64}', item['sha256']) or not isinstance(item['size'], int) or item['size'] < 0:
            raise ValueError('Invalid manifest entry')
    return data


def checked(stream, item):
    if digest(stream) != item['sha256']:
        raise ValueError('SHA-256 mismatch: ' + item['path'] + '; use the documented tested inputs')


def prepare(args, archive):
    """Validate ALL local inputs before making any network connection."""
    plan = []
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate entries in base ZIP')
    for item in manifest('runtime.json'):
        member = 'WoWForever-PS5/runtime/wowps5/' + item['path']
        info = archive.getinfo(member)
        if info.file_size != item['size'] or ((info.external_attr >> 16) & 0o170000) == 0o120000:
            raise ValueError('Invalid runtime ZIP entry')
        with archive.open(member) as stream:
            checked(stream, item)
        remote = ROOT + '/' + item['path'].replace('prefix/drive_c/', 'prefix/dosdevices/c:/')
        plan.append((('zip', member), confined(remote), item))
    for group, directory, prefix in [('game.json', args.game, GAME), ('cache.json', args.cache, CACHE)]:
        for item in manifest(group):
            path = local_file(directory, item['path'])
            if path.stat().st_size != item['size']:
                raise ValueError('Size mismatch: ' + item['path'])
            with path.open('rb') as stream:
                checked(stream, item)
            plan.append((('file', path), confined(prefix + item['path']), item))
    for item in manifest('bundle.json'):
        path = local_file(args.bundle, item['path'])
        with path.open('rb') as stream:
            checked(stream, item)
        if item['path'].startswith('title/'):
            remote = TITLE + '/' + item['path'][6:]
        elif item['path'].startswith('runtime/'):
            remote = ROOT + '/' + item['path'][8:].replace('prefix/drive_c/', 'prefix/dosdevices/c:/')
        else:
            raise ValueError('Unexpected bundle root')
        plan.append((('file', path), confined(remote), item))
    compiler = local_file(args.compiler.parent, args.compiler.name)
    expected = {'path': 'd3dcompiler_47.dll', 'size': 4741488,
                'sha256': 'a05f99734f7c4822fefc12b367af21fd0976ed6608752fb1e1e80b6ece7ecbbb'}
    with compiler.open('rb') as stream:
        checked(stream, expected)
    plan.append((('file', compiler), GAME + expected['path'], expected))
    # Prevent later phases from silently replacing an earlier input.
    destinations = [remote.casefold() for _, remote, _ in plan]
    if len(destinations) != len(set(destinations)):
        raise ValueError('Overlapping install destinations')
    return sorted(plan, key=lambda x: (x[1] == TITLE + '/sce_sys/param.json', x[1] == TITLE + '/eboot.bin', x[1]))


class Console:
    def __init__(self, host, port):
        ip = ipaddress.ip_address(host)
        if ip.version != 4 or not any(ip in ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')):
            raise ValueError('--host must be a private IPv4 LAN address')
        self.ftp = ftplib.FTP(timeout=30)
        self.ftp.connect(str(ip), port)
        self.ftp.login()
        self.ftp.sendcmd('SELF')
        self.ftp.voidcmd('TYPE I')

    def exists(self, path):
        try:
            self.ftp.cwd(path)
            self.ftp.cwd('/')
            return True
        except ftplib.error_perm as error:
            if str(error).startswith('550'):
                return False
            raise

    def remote_hash(self, remote):
        confined(remote)
        h = hashlib.sha256()
        try:
            self.ftp.retrbinary('RETR ' + remote, h.update, blocksize=BLOCK)
        except ftplib.error_perm as error:
            if str(error).startswith('550'):
                return None
            raise
        return h.hexdigest()

    def mkdirs(self, remote):
        parts = PurePosixPath(confined(remote)).parent.parts
        for n in range(2, len(parts) + 1):
            folder = str(PurePosixPath(*parts[:n]))
            try:
                self.ftp.mkd(folder)
            except ftplib.error_perm as error:
                if not str(error).startswith('550') or not self.exists(folder):
                    raise

    def put(self, remote, stream, sha):
        confined(remote)
        if self.remote_hash(remote) == sha:
            return 'verified existing'
        self.mkdirs(remote)
        partial = remote + '.reskate-part'
        # Restart an interrupted FILE; completed files are skipped only by hash.
        self.ftp.storbinary('STOR ' + partial, stream, blocksize=BLOCK)
        if self.remote_hash(partial) != sha:
            raise RuntimeError('Console readback mismatch: ' + remote)
        self.ftp.rename(partial, remote)
        return 'uploaded and verified'

    def claim(self):
        expected = hashlib.sha256(MARKER).hexdigest()
        # Validate BOTH destinations before creating or replacing anything.
        for directory in (ROOT, TITLE):
            marker = directory + '/.reskate-installer'
            if self.exists(directory) and self.remote_hash(marker) != expected:
                raise RuntimeError('Existing unrecognized installation; refusing to overwrite ' + directory)
        for directory in (ROOT, TITLE):
            self.put(directory + '/.reskate-installer', io.BytesIO(MARKER), expected)

    def close(self):
        with contextlib.suppress(Exception):
            self.ftp.quit()
        self.ftp.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True, help='Unmodified WoWForever-PS5 v0.1.0 ZIP')
    parser.add_argument('--game', type=Path, required=True, help='Your compatible ReSkate 2.0.5 game directory')
    parser.add_argument('--cache', type=Path, required=True, help='Your ReSkate/cache/25414733 directory')
    parser.add_argument('--compiler', type=Path, required=True, help='Your Windows SDK x64 d3dcompiler_47.dll')
    parser.add_argument('--bundle', type=Path, default=HERE / 'bundle')
    parser.add_argument('--host', help='PS5 LAN IPv4 address; required only with --install')
    parser.add_argument('--port', type=int, default=2121)
    parser.add_argument('--install', action='store_true', help='Write verified files to the PS5')
    parser.add_argument('--console-at-home', action='store_true', help='Confirm ReSkate is fully closed')
    args = parser.parse_args()
    if args.install and (not args.host or not args.console_at_home):
        parser.error('--install requires --host and --console-at-home')
    if not 1 <= args.port <= 65535:
        parser.error('Invalid FTP port')
    print('EXPERIMENTAL: loading observed; gameplay unverified; hangs/crashes remain.', flush=True)
    with args.base.open('rb') as stream:
        if digest(stream) != BASE_SHA:
            raise ValueError('Base ZIP must be the pinned v0.1.0 release (see README)')
    with zipfile.ZipFile(args.base) as archive:
        print('Verifying local inputs. This reads about 14 GiB.', flush=True)
        plan = prepare(args, archive)
        print(f'Validated {len(plan)} files, {sum(item[2]["size"] for item in plan) / 2**30:.2f} GiB.')
        print('Destinations: ' + ROOT + ' and ' + TITLE)
        if not args.install:
            print('Dry run complete. No console connection or writes were made.')
            return
        console = Console(args.host, args.port)
        try:
            console.claim()
            for number, (source, remote, item) in enumerate(plan, 1):
                with archive.open(source[1]) if source[0] == 'zip' else source[1].open('rb') as stream:
                    status = console.put(remote, stream, item['sha256'])
                print(f'[{number}/{len(plan)}] {status}: {remote}', flush=True)
        finally:
            console.close()
    print('Copy verified. Register /data/homebrew/PPSA99223 with your homebrew manager, then launch ReSkate.')
    print('Do not share your game directory, cache, prefix, or unredacted logs.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, ftplib.Error, zipfile.BadZipFile, KeyError) as error:
        print('Stopped: ' + str(error), file=sys.stderr)
        sys.exit(1)
