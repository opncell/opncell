#!/usr/local/bin/python3.12
"""Stage and verify the 26.7.2_6 public package repository before root activation."""
from pathlib import Path
import json,hashlib,shutil,subprocess,urllib.request,urllib.parse
home=Path('/usr/home/codex/opncell-release')
release=home/'26.7.2_6'
source=release/'packages'
target=Path('/usr/local/www/apache24/data/cellular/releases/26.7.2_6/repo')
url='http://repo.opncell.io/releases/26.7.2_6/repo'
lock=json.loads((release/'packages.lock.json').read_text())
# Keep both supported ABI endpoints available before publishing a new stable link.
abi_targets = {
    'FreeBSD:14:amd64': '../../../archive/legacy-25.8',
    'FreeBSD:15:amd64': '.',
}
for abi, relative_target in abi_targets.items():
    link = target / abi
    if not link.exists():
        link.symlink_to(relative_target, target_is_directory=True)
    assert link.resolve() == (target / relative_target).resolve(), link
(target/'All').mkdir(parents=True,exist_ok=True)
for item in lock:
    name=f"{item['name']}-{item['version']}.pkg"
    src=source/'All'/name
    dst=target/'All'/name
    with src.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256'],name
    shutil.copyfile(src,dst)
    dst.chmod(0o644)
# The catalog is installed after every package is present.
for file in source.iterdir():
    if file.is_file():
        shutil.copyfile(file,target/file.name)
        (target/file.name).chmod(0o644)
verified=[]
for item in lock:
    name=f"{item['name']}-{item['version']}.pkg"
    with urllib.request.urlopen(url+'/All/'+urllib.parse.quote(name),timeout=30) as response:
        digest=hashlib.sha256()
        for chunk in iter(lambda:response.read(1024*1024),b''):
            digest.update(chunk)
        assert digest.hexdigest()==item['sha256'],name
    verified.append(name)
check=home/'public-check'
for name in ['repos','db','cache']:
    (check/name).mkdir(parents=True,exist_ok=True)
(check/'repos/staged.conf').write_text('OPNcellStaged: { url: "'+url+'", enabled: yes }\n')
base=['pkg','-o','INSTALL_AS_USER=yes','-o','PKG_DBDIR='+str(check/'db'),
      '-o','PKG_CACHEDIR='+str(check/'cache'),'-o','REPOS_DIR='+str(check/'repos')]
update=subprocess.run(base+['update','-f','-r','OPNcellStaged'],text=True,capture_output=True)
assert update.returncode==0,update.stdout+update.stderr
preview=subprocess.run(base+['install','-n','-r','OPNcellStaged','os-cellular'],text=True,capture_output=True)
output=preview.stdout+preview.stderr
assert 'Number of packages to be installed: 48' in output and 'missing dependency' not in output,output
(check/'install-preview.txt').write_text(output)
versions=subprocess.check_output(base+['rquery','-r','OPNcellStaged','%n-%v',
    'os-cellular','mongodb80','open5gs','opncell-mongosh'],text=True)
report={'staged_url':url,'http_package_hashes_verified':len(verified),'catalog_versions':versions.splitlines(),
        'dependency_preview':'48 packages resolved; local integrity check recorded separately','previous_live_target':'releases/26.7/repo'}
# Validate the ABI routes with separate catalog databases. These OSVERSION
# settings simulate clients and are never used to install packages on this host.
abi_versions = {}
for abi, osversion in [('FreeBSD:14:amd64', '1403000'), ('FreeBSD:15:amd64', '1501000')]:
    abi_check = check / abi
    for directory in ['repos', 'db', 'cache']:
        (abi_check / directory).mkdir(parents=True, exist_ok=True)
    (abi_check / 'repos/OPNcell.conf').write_text(
        'OPNcell: { url: "' + url + '/${ABI}", enabled: yes }\n')
    abi_command = ['pkg', '-o', 'INSTALL_AS_USER=yes', '-o', 'ABI=' + abi,
        '-o', 'OSVERSION=' + osversion, '-o', 'PKG_DBDIR=' + str(abi_check / 'db'),
        '-o', 'PKG_CACHEDIR=' + str(abi_check / 'cache'),
        '-o', 'REPOS_DIR=' + str(abi_check / 'repos')]
    subprocess.run(abi_command + ['update', '-f', '-r', 'OPNcell'], check=True)
    abi_versions[abi] = subprocess.check_output(
        abi_command + ['rquery', '-r', 'OPNcell', '%n-%v %q', 'os-cellular'], text=True).splitlines()
report['abi_catalog_checks'] = abi_versions
(release/'public-staging-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
