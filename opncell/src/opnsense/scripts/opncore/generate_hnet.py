#!/usr/local/bin/python3

import sys
import json
import base64
import subprocess
from pathlib import Path
import yaml
import os


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

    with open(yaml_file, "w") as f:
        yaml.safe_dump(
            config,
            f,
            sort_keys=False,
            default_flow_style=False
        )

    return result == "ok"

def main():

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


    hnet_dir = Path("/usr/ports/open5gs/install/etc/open5gs/hnet")
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

    # Generate private key

    if scheme == 1:
        run_command([
            "openssl", "genpkey",
            "-algorithm", algo,
            "-out", str(priv_key_path)
        ])
    else:
        run_command([
            "openssl", "ecparam",
            "-name", algo,
            "-genkey",
            "-noout",
            "-out", str(priv_key_path)
        ])


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
        pub_key_path.write_text(pub_pem)

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
    hex_path.write_text(hex_pub)

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
        "public_key_hex": hex_pub }

    print(json.dumps(response))

if __name__ == "__main__":
    main()