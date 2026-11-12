#!/usr/local/bin/python3

import json
import subprocess
import os
import tempfile
from pathlib import Path

PUBLIC_DIRECTORY = Path("/usr/local/etc/open5gs/hnet/public")

UDM_YAML = "/usr/local/etc/open5gs/udm.yaml"


def run_command(cmd, binary=False):
    result = subprocess.run(cmd, capture_output=True, text=not binary, check=True)
    return result.stdout


def derive_public_key(priv_key_path, scheme):
    from hnet_management import material, number
    number(scheme, (1, 2))
    public = material(Path(priv_key_path).read_bytes(), scheme)
    return public['pem'], public['hex']



def store_public_keys(hnet_id, pub_pem, hex_pub, directory=None):
    directory = Path(directory) if directory is not None else PUBLIC_DIRECTORY
    if directory.is_symlink():
        raise ValueError("Public key directory must not be a symbolic link")
    directory.mkdir(mode=0o755, parents=True, exist_ok=True)
    hnet_id = int(hnet_id)
    if not 1 <= hnet_id <= 255:
        raise ValueError("Hnet key ID must be between 1 and 255")
    pem = directory / f'hnet_pubkey_{hnet_id}.pub'
    hex_path = pem.with_suffix('.pub.hex')
    for target, content in ((pem, pub_pem), (hex_path, hex_pub)):
        with tempfile.NamedTemporaryFile(mode='w', dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                os.fchmod(stream.fileno(), 0o644)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                stream.close()
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
    return pem, hex_path


def main():
    import yaml
    try:
        with open(UDM_YAML, "r") as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(json.dumps({"result": "ok", "entries": []}))
        return

    hnet = config.get("udm", {}).get("hnet", []) or []
    entries = []

    for entry in hnet:
        priv_key_path = entry.get("key")
        scheme = entry.get("scheme", 2)
        item = {
            "id": entry.get("id"),
            "scheme": scheme,
            "private_key_path": priv_key_path,
        }

        try:
            from hnet_management import material
            public = material(Path(priv_key_path).read_bytes(), scheme)
            pub_pem, hex_pub = public['pem'], public['hex']
            pem, hex_path = store_public_keys(entry.get("id"), pub_pem, hex_pub)
            item["public_key_path"] = str(pem)
            item["public_key_hex_path"] = str(hex_path)
            item["fingerprint"] = public['fingerprint']
            item["public_key_pem"] = pub_pem
            item["public_key_hex"] = hex_pub
        except (subprocess.CalledProcessError, OSError, TypeError, ValueError) as e:
            item["error"] = f"Could not prepare public key: {e}"

        entries.append(item)

    print(json.dumps({"result": "ok", "entries": entries}))


if __name__ == "__main__":
    main()
