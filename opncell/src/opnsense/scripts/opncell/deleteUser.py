#!/usr/local/bin/python3

import json
import os
import re
import shutil
import subprocess
import sys

from subscriber_identity import mongosh_failure


def main():
    try:
        data = json.loads(sys.argv[1])
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        imsi = data["imsi"]
        if not isinstance(imsi, str) or not re.fullmatch(r"[0-9]{5,16}", imsi):
            print(json.dumps({"result": "failed", "message": "Invalid subscriber IMSI"}))
            return
        mongosh = shutil.which("mongosh")
        if not mongosh:
            print(json.dumps({"result": "failed", "message": "MongoDB Shell (mongosh) is required for subscriber management"}))
            return
        command = """
try {
    const result = db.subscribers.deleteOne({imsi: IMSI});
    if (!result.acknowledged) {
        print(JSON.stringify({result: "failed", message: "MongoDB did not acknowledge the deletion"}));
    } else if (result.deletedCount === 1) {
        print(JSON.stringify({result: "deleted"}));
    } else {
        print(JSON.stringify({result: "not found", message: "Subscriber was not found in MongoDB. Refresh the subscriber list."}));
    }
} catch (error) {
    print(JSON.stringify({result: "failed", message: error.code === 13
        ? "MongoDB denied permission to delete subscribers."
        : "MongoDB rejected the deletion. Check the MongoDB log."}));
}
"""
        uri = os.environ.get("DB_URI") or "mongodb://127.0.0.1:27017/open5gs"
        output = subprocess.run(
            [mongosh, "--quiet", uri, "--eval", "const IMSI = " + json.dumps(imsi) + ";\n" + command],
            capture_output=True, text=True, check=False,
        )
        lines = output.stdout.strip().splitlines()
        if not lines:
            print(json.dumps({"result": "failed", "message": mongosh_failure(output.stderr, operation="delete")}))
            return
        print(json.dumps(json.loads(lines[-1])))
    except (IndexError, KeyError, TypeError, ValueError):
        print(json.dumps({"result": "failed", "message": "Deletion was not confirmed. Refresh the subscriber list before retrying."}))
    except OSError:
        print(json.dumps({"result": "failed", "message": "Could not execute MongoDB Shell. Check its installation and permissions."}))


if __name__ == "__main__":
    main()
