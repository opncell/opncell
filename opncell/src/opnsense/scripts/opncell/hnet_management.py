#!/usr/local/bin/python3
"""Transactional Hnet key management and authenticated, passphrase-encrypted bundles."""
import base64
import copy
import datetime
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile
import tempfile
import uuid

ITERATIONS = 300000
MAX_BUNDLE = 1048576
PREFIXES = {1: bytes.fromhex('302a300506032b656e032100'),
            2: bytes.fromhex('3039301306072a8648ce3d020106082a8648ce3d030107032200')}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def number(value, allowed=None):
    if type(value) is not int or not 1 <= value <= 255 or (allowed and value not in allowed):
        raise ValueError('Invalid Hnet key ID or protection scheme')
    return value


def openssl(arguments, data):
    result = subprocess.run(['openssl', *arguments], input=data, capture_output=True, timeout=15)
    if result.returncode:
        raise ValueError('Invalid or unsupported Hnet private key')
    return result.stdout


def material(private, scheme):
    number(scheme, (1, 2))
    if not isinstance(private, bytes) or not 32 <= len(private) <= 16384:
        raise ValueError('Invalid Hnet private key size')
    if private.splitlines()[0] not in (b'-----BEGIN PRIVATE KEY-----', b'-----BEGIN EC PRIVATE KEY-----'):
        raise ValueError('Hnet private keys must be unencrypted PEM keys')
    # No private output or subprocess diagnostics are returned to the caller.
    der = openssl(['pkey', '-pubout', '-outform', 'DER'] if scheme == 1 else
                  ['ec', '-pubout', '-conv_form', 'compressed', '-outform', 'DER'], private)
    size = 32 if scheme == 1 else 33
    if not der.startswith(PREFIXES[scheme]) or len(der) != len(PREFIXES[scheme]) + size:
        raise ValueError('Private key does not match the selected protection scheme')
    pem = openssl(['pkey', '-pubin', '-inform', 'DER', '-outform', 'PEM'], der).decode()
    return {'fingerprint': hashlib.sha256(der).hexdigest(), 'pem': pem, 'hex': der[-size:].hex()}


def passphrase(value):
    if not isinstance(value, str) or not 12 <= len(value) <= 1024 or any(c in value for c in '\r\n\0'):
        raise ValueError('Use a bundle passphrase of 12–1024 characters without line breaks')
    return value.encode()


def cipher(data, password, decrypt=False):
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, password + b'\n')
        os.close(write_fd)
        write_fd = None
        command = ['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-iter', str(ITERATIONS),
                   '-md', 'sha256', '-pass', 'fd:' + str(read_fd)]
        if decrypt:
            command.append('-d')
        result = subprocess.run(command, input=data, capture_output=True, pass_fds=(read_fd,), timeout=30)
        if result.returncode:
            raise ValueError('Unable to encrypt or decrypt the Hnet bundle')
        return result.stdout
    finally:
        os.close(read_fd)
        if write_fd is not None:
            os.close(write_fd)


def encrypt_bundle(entries, phrase):
    password = passphrase(phrase)
    salt = os.urandom(32)
    body = {'format': 'opncell-hnet', 'version': 1, 'cipher': 'AES-256-CBC+HMAC-SHA256',
            'iterations': ITERATIONS, 'salt': base64.b64encode(salt).decode(),
            'payload': base64.b64encode(cipher(canonical({'keys': entries}), password)).decode()}
    key = hashlib.pbkdf2_hmac('sha256', password, salt, ITERATIONS, 32)
    body['mac'] = hmac.new(key, canonical(body), 'sha256').hexdigest()
    return body


def decrypt_bundle(bundle, phrase):
    password = passphrase(phrase)
    try:
        if not isinstance(bundle, dict) or len(canonical(bundle)) > MAX_BUNDLE:
            raise ValueError()
        body = dict(bundle)
        signature = body.pop('mac')
        if set(body) != {'format', 'version', 'cipher', 'iterations', 'salt', 'payload'}:
            raise ValueError()
        if (body['format'], body['version'], body['cipher'], body['iterations']) != (
                'opncell-hnet', 1, 'AES-256-CBC+HMAC-SHA256', ITERATIONS):
            raise ValueError()
        salt = base64.b64decode(body['salt'], validate=True)
        encrypted = base64.b64decode(body['payload'], validate=True)
        if len(salt) != 32 or not 32 <= len(encrypted) <= MAX_BUNDLE:
            raise ValueError()
        key = hashlib.pbkdf2_hmac('sha256', password, salt, ITERATIONS, 32)
        if not isinstance(signature, str) or not hmac.compare_digest(signature, hmac.new(key, canonical(body), 'sha256').hexdigest()):
            raise ValueError()
        payload = json.loads(cipher(encrypted, password, decrypt=True))
    except (ValueError, TypeError, KeyError, UnicodeError):
        raise ValueError('Incorrect passphrase, damaged bundle or unsupported bundle format') from None
    keys = payload.get('keys') if isinstance(payload, dict) else None
    if not isinstance(keys, list) or not 1 <= len(keys) <= 255:
        raise ValueError('The bundle contains no valid Hnet key set')
    seen = set()
    for entry in keys:
        if not isinstance(entry, dict) or set(entry) != {'id', 'scheme', 'private_key', 'fingerprint'}:
            raise ValueError('Invalid Hnet bundle entry')
        key_id = number(entry['id']); scheme = number(entry['scheme'], (1, 2))
        if key_id in seen:
            raise ValueError('Duplicate key IDs in the Hnet bundle')
        seen.add(key_id)
        if not isinstance(entry['private_key'], str):
            raise ValueError('Invalid private key in bundle')
        public = material(entry['private_key'].encode(), scheme)
        if public['fingerprint'] != entry['fingerprint']:
            raise ValueError('Bundle public-key fingerprint does not match its private key')
    return keys


class HnetManager:
    def __init__(self, root=Path('/'), runtime=None):
        self.root = Path(root)
        self.config = self.root / 'usr/local/etc/open5gs/udm.yaml'
        self.directory = self.config.with_name('hnet')
        self.public = self.directory / 'public'
        self.backups = self.root / 'root/opncell-hnet-recovery'
        self.runtime = runtime or self.udm

    @staticmethod
    def udm(action):
        response = subprocess.run(['configctl', 'udmd', action], capture_output=True, text=True, timeout=45)
        if response.returncode:
            raise ValueError('Unable to inspect or update the UDM service')
        if action == 'status':
            if 'is running' in response.stdout:
                return True
            if 'not running' in response.stdout:
                return False
            raise ValueError('Cannot determine whether UDM is running')
        return response.stdout.strip() == 'OK'

    def read_private(self, path):
        path = Path(path)
        if self.root != Path('/'):
            path = self.root / str(path).lstrip('/')
        if path.parent != self.directory or path.is_symlink():
            raise ValueError('Hnet private keys must be regular files in the managed Hnet directory')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError('Hnet key is not a regular file')
            return stream.read(16385)

    def load(self):
        import yaml
        config = yaml.safe_load(self.config.read_text()) or {}
        if not isinstance(config, dict) or not isinstance(config.get('udm'), dict):
            raise ValueError('UDM configuration is missing or invalid')
        entries = config['udm'].get('hnet') or []
        if not isinstance(entries, list):
            raise ValueError('Invalid UDM Hnet key list')
        seen = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError('Invalid Hnet entry')
            key_id = number(entry.get('id')); number(entry.get('scheme'), (1, 2))
            if not isinstance(entry.get('key'), str) or not entry['key'].startswith('/'):
                raise ValueError('Invalid Hnet private-key reference')
            if key_id in seen:
                raise ValueError('Duplicate Hnet key IDs in UDM')
            seen.add(key_id)
        return config, entries

    def snapshot(self, entries):
        rows = []
        for entry in entries:
            try:
                fingerprint = material(self.read_private(entry['key']), entry['scheme'])['fingerprint']
            except (ValueError, OSError):
                fingerprint = 'unavailable'
            rows.append({'id': entry['id'], 'scheme': entry['scheme'], 'fingerprint': fingerprint})
        rows.sort(key=lambda e: e['id'])
        return rows, hashlib.sha256(canonical(rows)).hexdigest()

    def backup(self):
        self.backups.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.backups.chmod(0o700)
        backup = self.backups / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex)
        backup.mkdir(mode=0o700)
        with os.fdopen(os.open(backup / 'hnet.tar.gz', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as out:
            with tarfile.open(fileobj=out, mode='w:gz') as archive:
                archive.add(self.config, arcname='udm.yaml')
                if self.directory.exists():
                    archive.add(self.directory, arcname='hnet', recursive=True)
        return backup

    def refresh(self, entries):
        from list_hnet import store_public_keys
        keep = set()
        for entry in entries:
            public = material(self.read_private(entry['key']), entry['scheme'])
            pem, hexfile = store_public_keys(entry['id'], public['pem'], public['hex'], self.public)
            keep.update((pem, hexfile))
        if self.public.exists():
            for path in self.public.glob('hnet_pubkey_*'):
                if re.fullmatch(r'hnet_pubkey_[0-9]+\.pub(?:\.hex)?', path.name) and path not in keep:
                    if path.is_file() or path.is_symlink():
                        path.unlink()

    def change(self, config, entries, incoming=None, delete_id=None):
        from atomic_yaml import replace_yaml
        updated = copy.deepcopy(config)
        new_entries = copy.deepcopy(entries)
        created = []
        backup = self.backup()
        running = self.runtime('status')
        try:
            if delete_id is not None:
                new_entries = [e for e in new_entries if e['id'] != delete_id]
            for entry in incoming or []:
                old = next((e for e in entries if e['id'] == entry['id']), None)
                if old:
                    try:
                        if old['scheme'] == entry['scheme'] and material(self.read_private(old['key']), old['scheme'])['fingerprint'] == entry['fingerprint']:
                            continue
                    except (OSError, ValueError):
                        pass
                self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
                path = self.directory / f"hnet-import-{entry['id']}-{uuid.uuid4().hex}.key"
                with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as out:
                    created.append(path)
                    out.write(entry['private_key'].encode()); out.flush(); os.fsync(out.fileno())
                configured_path = '/' + str(path.relative_to(self.root))
                new_entries = [e for e in new_entries if e['id'] != entry['id']]
                new_entries.append({'id': entry['id'], 'scheme': entry['scheme'], 'key': configured_path})
            new_entries.sort(key=lambda e: e['id'])
            updated['udm']['hnet'] = new_entries
            replace_yaml(self.config, updated)
            self.refresh(new_entries)
            if running and (not self.runtime('restart') or not self.runtime('status')):
                raise ValueError('UDM did not restart with the changed key set')
        except Exception as error:
            try:
                replace_yaml(self.config, config)
                self.refresh(entries)
                if running:
                    self.runtime('restart')
                    if not self.runtime('status'):
                        raise ValueError('UDM remains stopped')
            except Exception:
                raise ValueError('Hnet update failed and recovery needs attention. Backup: ' + str(backup)) from None
            for path in created:
                path.unlink(missing_ok=True)
            raise ValueError('Hnet update failed; previous configuration restored. Backup: ' + str(backup)) from error
        # Only delete decommissioned managed files after config and runtime commit.
        referenced = {e['key'] for e in new_entries}
        for old in entries:
            if old.get('key') not in referenced:
                path = Path(old.get('key', ''))
                if self.root != Path('/'):
                    path = self.root / str(path).lstrip('/')
                if path.parent == self.directory and not path.is_symlink():
                    path.unlink(missing_ok=True)
        return {'result': 'ok', 'message': 'Hnet keys updated', 'udm_restarted': running,
                'backup': str(backup), 'entries': self.snapshot(new_entries)[0]}

    def handle(self, request):
        operation = request.get('operation')
        if operation not in ('export', 'plan', 'import', 'delete', 'generate'):
            raise ValueError('Invalid Hnet operation')
        if not self.config.is_file() or self.config.is_symlink() or self.directory.is_symlink():
            raise ValueError('Hnet configuration or directory is missing or invalid')
        incoming = decrypt_bundle(request.get('bundle'), request.get('passphrase')) if operation in ('plan', 'import') else None
        with open(str(self.config) + '.opncell.lock', 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            config, entries = self.load()
            rows, token = self.snapshot(entries)
            if operation == 'generate':
                scheme = number(request.get('scheme'), (1, 2))
                key_id = max((e['id'] for e in entries), default=0) + 1
                number(key_id)
                private = openssl(['genpkey', '-algorithm', 'X25519'] if scheme == 1 else
                                  ['ecparam', '-name', 'prime256v1', '-genkey', '-noout'], b'')
                public = material(private, scheme)
                self.change(config, entries, incoming=[{'id': key_id, 'scheme': scheme,
                            'private_key': private.decode(), 'fingerprint': public['fingerprint']}])
                _, configured = self.load()
                entry = next(e for e in configured if e['id'] == key_id)
                return {'result': 'ok', 'id': key_id, 'scheme': scheme,
                        'private_key_path': entry['key'],
                        'public_key_path': str(self.public / f'hnet_pubkey_{key_id}.pub'),
                        'public_key_hex_path': str(self.public / f'hnet_pubkey_{key_id}.pub.hex'),
                        'public_key_pem': public['pem'], 'public_key_hex': public['hex']}
            if operation == 'export':
                if not entries:
                    raise ValueError('No Hnet keys are available to export')
                keys = []
                for entry in entries:
                    private = self.read_private(entry['key'])
                    public = material(private, entry['scheme'])
                    keys.append({'id': entry['id'], 'scheme': entry['scheme'], 'private_key': private.decode(), 'fingerprint': public['fingerprint']})
                return {'result': 'ok', 'bundle': encrypt_bundle(keys, request.get('passphrase'))}
            if operation in ('plan', 'import'):
                existing = {e['id']: e for e in rows}
                preview = []
                for entry in incoming:
                    old = existing.get(entry['id'])
                    same = old and old['scheme'] == entry['scheme'] and old['fingerprint'] == entry['fingerprint']
                    preview.append({'id': entry['id'], 'scheme': entry['scheme'], 'fingerprint': entry['fingerprint'],
                                    'action': 'unchanged' if same else 'replace' if old else 'add'})
                if operation == 'plan':
                    return {'result': 'ok', 'state': token, 'entries': preview,
                            'retained_ids': [e['id'] for e in rows if e['id'] not in {k['id'] for k in incoming}]}
                if request.get('state') != token:
                    raise ValueError('Hnet keys changed since preview. Preview the bundle again')
                if any(e['action'] == 'replace' for e in preview) and request.get('replace_conflicts') is not True:
                    raise ValueError('Conflicting Hnet key IDs require explicit replacement approval')
                if all(e['action'] == 'unchanged' for e in preview):
                    self.refresh(entries)
                    return {'result': 'ok', 'message': 'Hnet keys already match; UDM was not restarted', 'udm_restarted': False}
                return self.change(config, entries, incoming=incoming)
            key_id = number(request.get('id'))
            entry = next((e for e in rows if e['id'] == key_id), None)
            if entry is None:
                raise ValueError('Hnet key ID no longer exists')
            if request.get('fingerprint') != entry['fingerprint']:
                raise ValueError('Hnet key changed. Refresh the list before deleting it')
            return self.change(config, entries, delete_id=key_id)


def load_request(path):
    if not re.fullmatch(r'/tmp/opncell-hnet-[a-zA-Z0-9]+', path):
        raise ValueError('Invalid Hnet request file')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
            raise ValueError('Hnet request must be a private regular file')
        value = stream.read(MAX_BUNDLE * 2 + 1)
        if len(value) > MAX_BUNDLE * 2:
            raise ValueError('Hnet request is too large')
        request = json.loads(value)
        if not isinstance(request, dict):
            raise ValueError('Invalid Hnet request')
        return request


if __name__ == '__main__':
    import sys
    try:
        if len(sys.argv) != 2:
            raise ValueError('Hnet request file required')
        print(json.dumps(HnetManager().handle(load_request(sys.argv[1]))))
    except (ValueError, OSError, subprocess.SubprocessError):
        # ValueErrors are constructed here and never contain private key material.
        error = sys.exc_info()[1]
        message = str(error) if isinstance(error, ValueError) else 'Unable to complete Hnet operation; check the service and file permissions'
        print(json.dumps({'result': 'failed', 'message': message}))
