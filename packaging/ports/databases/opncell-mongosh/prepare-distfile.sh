#!/bin/sh
set -eu
destination=${1:?Pass the absolute DISTDIR path}
case "$destination" in
    /*) ;;
    *) echo "DISTDIR must be absolute" >&2; exit 1 ;;
esac
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT
name=opncell-mongosh-2.14.0
mkdir "$build_dir/$name"
cd "$build_dir/$name"
printf '%s\n' '{"private":true,"dependencies":{"mongosh":"2.14.0"}}' > package.json
npm install --registry=https://registry.npmjs.org --omit=dev --ignore-scripts --no-audit --no-fund
entry=$(node -p 'require("./node_modules/mongosh/package.json").bin.mongosh')
case "$entry" in
    bin/mongosh.js|./bin/mongosh.js) ;;
    *) echo "Unexpected mongosh entry point: $entry" >&2; exit 1 ;;
esac
test "$(node "node_modules/mongosh/$entry" --version)" = 2.14.0
# The launcher invokes Node directly. npm's executable links are unnecessary.
rm -rf node_modules/.bin
tar -C "$build_dir" -czf "$destination/$name.tar.gz" "$name"
