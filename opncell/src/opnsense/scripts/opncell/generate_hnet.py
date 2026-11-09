#!/usr/local/bin/python3

import sys
import json
import base64
import fcntl
import subprocess
from pathlib import Path
import yaml
import os

from atomic_yaml import replace_yaml


response = {}
result = "ok"

def run_command(cmd, binary=False):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=not binary,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr}", file=sys.stderr)
        sys.exit(1)


UDM_YAML = "/usr/local/etc/open5gs/udm.yaml"

def allocate_hnet_id(yaml_file):
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f) or {}

    hnet = config.setdefault("udm", {}).setdefault("hnet", [])

    if not hnet:
        return 1

    return max(entry["id"] for entry in hnet) + 1


def append_hnet_entry(yaml_file, hnet_id, scheme, key_path):
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f) or {}

    config.setdefault("udm", {})
    config["udm"].setdefault("hnet", [])

    config["udm"]["hnet"].append({
        "id": hnet_id,
        "scheme": scheme,
        "key": str(key_path)
    })

    replace_yaml(yaml_file, config)

    return result == "ok"

def generate(created_files):

    if len(sys.argv) < 2:
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)

    try:
        decoded = base64.b64decode(sys.argv[1]).decode()
        data = json.loads(decoded)
    except Exception as e:
        print(f"Error decoding input: {e}", file=sys.stderr)
        sys.exit(1)

    try:

        scheme = int(data.get("scheme", 2))
        if scheme not in (1, 2):
            raise ValueError("Invalid Hnet scheme")
        hnet_id = allocate_hnet_id(UDM_YAML)

        path_str = data.get("pubkey_path") or data.get("filepath")
        if not path_str:
            print("Error: pubkey_path is required", file=sys.stderr)
            sys.exit(1)

        pubkey_path = path_str.replace("\\/", "/")
        pubkey_path = f"{pubkey_path}{hnet_id}.pub"
        dir_path = os.path.dirname(pubkey_path)

        os.makedirs(dir_path, mode=0o755, exist_ok=True)


    except Exception as e:
        print(json.dumps({
            "result": "Failed",
            "error": repr(e)
        }))
        return


    hnet_dir = Path(UDM_YAML).with_name("hnet")
    hnet_dir.mkdir(parents=True, exist_ok=True)

    # Key selection

    if scheme == 1:
        key_type = "curve25519"
        algo = "X25519"
        priv_filename = f"{key_type}-{hnet_id}.key"
    else:
        key_type = "secp256r1"
        algo = "prime256v1"
        priv_filename = f"{key_type}-{hnet_id}.key"

    priv_key_path = hnet_dir / priv_filename
    pub_key_path = Path(pubkey_path)

    # Create the private key exclusively with restrictive permissions.
    command = (
        ["openssl", "genpkey", "-algorithm", algo]
        if scheme == 1 else
        ["openssl", "ecparam", "-name", algo, "-genkey", "-noout"]
    )
    private_key = run_command(command, binary=True)
    with os.fdopen(os.open(priv_key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as key:
        created_files.append(priv_key_path)
        key.write(private_key)

    # Generate public key PEM... rare case it's needed but, leave no stone unturned :)

    if scheme == 1:
        pub_pem = run_command([
            "openssl", "pkey",
            "-in", str(priv_key_path),
            "-pubout"
        ])
    else:
        pub_pem = run_command([
            "openssl", "ec",
            "-in", str(priv_key_path),
            "-pubout",
            "-conv_form", "compressed"
        ])

    try:
        with pub_key_path.open("x", encoding="utf-8") as public_key:
            created_files.append(pub_key_path)
            public_key.write(pub_pem)

    except Exception as e:
        print(json.dumps({
            "result": "Failed",
            "error": repr(e)
        }))
        return

    # Generate HEX public key
    if scheme == 1:
        der = run_command([
            "openssl", "pkey",
            "-in", str(priv_key_path),
            "-pubout",
            "-outform", "DER"
        ], binary=True)

        hex_pub = der[-32:].hex()

    else:
        der = run_command([
            "openssl", "ec",
            "-in", str(priv_key_path),
            "-pubout",
            "-outform", "DER"
        ], binary=True)

        hex_pub = der[-33:].hex()

    hex_path = pub_key_path.with_suffix(".pub.hex")
    with hex_path.open("x", encoding="utf-8") as public_hex:
        created_files.append(hex_path)
        public_hex.write(hex_pub)

    try:

         append_hnet_entry(
            UDM_YAML,
            hnet_id,
            scheme,
            priv_key_path
        )
    except Exception as e:
        print(json.dumps({
            "result": "Failed",
            "error": repr(e)
        }))
        return


    if result != "ok":
        print(json.dumps(result))
        return

    response = {
        "result": result,
        "id": hnet_id,
        "scheme": scheme,
        "private_key_path":str(priv_key_path),
        "public_key_path": str(pub_key_path),
        "public_key_hex_path": str(hex_path),
        "public_key_hex": hex_pub,
        "public_key_pem": pub_pem,
    }

    created_files.clear()
    print(json.dumps(response))

if __name__ == "__main__":
    try:
        # Use a separate lock file because udm.yaml is replaced atomically.
        with open(UDM_YAML + ".opncell.lock", "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            created_files = []
            try:
                generate(created_files)
            finally:
                for path in reversed(created_files):
                    path.unlink(missing_ok=True)
    except OSError:
        print(json.dumps({"result": "Failed", "error": "Could not write Hnet key files"}))
