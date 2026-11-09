#!/usr/local/bin/python3

import json
import subprocess
import yaml

UDM_YAML = "/usr/local/etc/open5gs/udm.yaml"


def run_command(cmd, binary=False):
    result = subprocess.run(cmd, capture_output=True, text=not binary, check=True)
    return result.stdout


def derive_public_key(priv_key_path, scheme):
    if scheme == 1:
        pub_pem = run_command(["openssl", "pkey", "-in", priv_key_path, "-pubout"])
        der = run_command(["openssl", "pkey", "-in", priv_key_path, "-pubout", "-outform", "DER"], binary=True)
        hex_pub = der[-32:].hex()
    else:
        pub_pem = run_command(["openssl", "ec", "-in", priv_key_path, "-pubout", "-conv_form", "compressed"])
        der = run_command(["openssl", "ec", "-in", priv_key_path, "-pubout", "-outform", "DER"], binary=True)
        hex_pub = der[-33:].hex()

    return pub_pem, hex_pub


def main():
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
        scheme = int(entry.get("scheme", 2))
        item = {
            "id": entry.get("id"),
            "scheme": scheme,
            "private_key_path": priv_key_path,
        }

        try:
            pub_pem, hex_pub = derive_public_key(priv_key_path, scheme)
            item["public_key_pem"] = pub_pem
            item["public_key_hex"] = hex_pub
        except (subprocess.CalledProcessError, FileNotFoundError, TypeError) as e:
            item["error"] = f"Could not read private key: {e}"

        entries.append(item)

    print(json.dumps({"result": "ok", "entries": entries}))


if __name__ == "__main__":
    main()
