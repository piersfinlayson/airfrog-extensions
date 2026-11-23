"""Checks the signed list in the current directory:

- manifest.json.minisig is a minisign signature of manifest.json by the
  manifest key in KEY_JS, airfrog-site's commissioning/manifest-key.js
- each extension image the list contains is the file at its address's path,
  with its size and SHA-256
- each image's header contains the list entry's name, model and WAMR
  version, and its extension metadata is the version's metadata and
  NAME/VERSION/extension-meta.json

Usage: python3 verify.py KEY_JS
"""
import base64
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import urllib.parse

# An Ed25519 public key's DER prefix (RFC 8410).
ED25519_DER = bytes.fromhex('302a300506032b6570032100')

failures = []


def fail(message):
    failures.append(message)


def verify(key, signature, body):
    """Whether signature is key's Ed25519 signature of body, checked with
    openssl."""
    with tempfile.TemporaryDirectory() as d:
        paths = {n: os.path.join(d, n) for n in ('key', 'sig', 'body')}
        for name, data in (('key', ED25519_DER + key), ('sig', signature), ('body', body)):
            with open(paths[name], 'wb') as f:
                f.write(data)
        return subprocess.run(['openssl', 'pkeyutl', '-verify', '-rawin', '-pubin', '-keyform', 'DER',
                               '-inkey', paths['key'], '-sigfile', paths['sig'], '-in', paths['body']],
                              capture_output=True).returncode == 0


def check_signature(key, body):
    if not os.path.exists('manifest.json.minisig'):
        return fail("manifest.json.minisig doesn't exist. Sign manifest.json with airfrog-site's "
                    'ci/release-extensions.py.')
    lines = open('manifest.json.minisig').read().split('\n')
    try:
        signature = base64.b64decode(lines[1], validate=True)
        global_signature = base64.b64decode(lines[3], validate=True)
        trusted = lines[2].removeprefix('trusted comment: ').encode()
    except (IndexError, ValueError):
        return fail("manifest.json.minisig isn't a minisign signature file.")
    if len(signature) != 74 or signature[:2] != b'Ed' or signature[2:10] != key[:8]:
        return fail("manifest.json.minisig isn't a signature by the manifest key.")
    if not verify(key, signature[10:], body) or not verify(key, global_signature, signature[10:] + trusted):
        fail("manifest.json.minisig doesn't verify. Sign manifest.json with airfrog-site's "
             'ci/release-extensions.py.')


def check_image(name, version, entry):
    label = '%s %s model %s wamr %s' % (name, version['metadata'].get('version'), entry['model'],
                                          entry['wamr'])
    path = urllib.parse.urlparse(entry['url']).path.lstrip('/')
    if not os.path.isfile(path):
        return fail("%s: %s doesn't exist." % (label, path))
    data = open(path, 'rb').read()
    if len(data) != entry['size'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
        return fail("%s: %s doesn't match its size and SHA-256." % (label, path))
    try:
        model, = struct.unpack_from('<H', data, 4)
        meta_offset, meta_len = struct.unpack_from('<II', data, 12)
        name_len, = struct.unpack_from('<H', data, 28)
        header_name = data[30:30 + name_len].decode()
        metadata = data[meta_offset:meta_offset + meta_len]
        wamr = '%d.%d.%d' % tuple(data[8:11])
    except (struct.error, UnicodeDecodeError):
        return fail("%s: %s isn't an extension image." % (label, path))
    if data[:4] != b'AFXI' or (header_name, model, wamr) != (name, entry['model'], entry['wamr']):
        return fail("%s: %s's header doesn't match the list." % (label, path))
    try:
        if json.loads(metadata) != version['metadata']:
            fail("%s: %s's extension metadata isn't the list's." % (label, path))
    except ValueError:
        return fail("%s: %s's extension metadata isn't JSON." % (label, path))
    meta_path = os.path.join(name, version['metadata'].get('version', ''), 'extension-meta.json')
    if not os.path.isfile(meta_path) or open(meta_path, 'rb').read() != metadata:
        fail("%s: %s isn't the image's extension metadata." % (label, meta_path))


def main():
    text = open(sys.argv[1]).read()
    match = re.search(r"MANIFEST_KEY = '([0-9a-f]*)'", text)
    if not match or len(match.group(1)) != 64:
        sys.exit("%s doesn't contain the manifest key." % sys.argv[1])
    key = bytes.fromhex(match.group(1))
    body = open('manifest.json', 'rb').read()
    check_signature(key, body)
    manifest = json.loads(body)
    if manifest.get('type') != 'extensions':
        fail("manifest.json isn't type extensions.")
    for name, extension in manifest.get('extensions', {}).items():
        for version in extension['versions']:
            for entry in version['images']:
                check_image(name, version, entry)
    if failures:
        sys.exit('\n'.join(failures))
    print('manifest.json and its extension images are valid.')


if __name__ == '__main__':
    main()
