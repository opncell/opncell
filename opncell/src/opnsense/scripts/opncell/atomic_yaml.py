import os
import stat
import tempfile
from pathlib import Path

import yaml


def replace_yaml(filename, data):
    """Write complete YAML before replacing the live file."""
    path = Path(filename).resolve(strict=True)
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("Configuration path must point to a regular file")

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=".opncell-", delete=False
    ) as staging:
        temporary_path = staging.name
        try:
            yaml.safe_dump(data, staging, sort_keys=False, default_flow_style=False)
            staging.flush()
            os.fchown(staging.fileno(), metadata.st_uid, metadata.st_gid)
            os.fchmod(staging.fileno(), stat.S_IMODE(metadata.st_mode))
            os.fsync(staging.fileno())
            staging.close()
            os.replace(temporary_path, path)
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)
