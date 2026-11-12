# Hnet key management

Choose a core as the authority for the Hnet key pairs and IDs used by your SIM/eSIM profiles. Export from that core and import the bundle on the other cores. Hnet transfers contain keys only; they do not copy subscribers, profiles or network settings.

## Export and import

Under **Cellular → Users → Hnet**, choose **Export keys**, enter and confirm a passphrase of at least 12 characters, then download the encrypted bundle. Share the bundle and passphrase separately.

On the destination, choose **Import keys**, select the bundle, enter its passphrase and select **Preview import**. The preview shows each incoming key's ID, protection scheme, public fingerprint and proposed action:

- **Add**: the ID does not exist on the destination.
- **Unchanged**: the ID, scheme and key already match; the private key is retained.
- **Replace**: the ID exists with a different scheme or key. Import requires the replacement checkbox.

Other destination IDs are retained. A changed key set invalidates an earlier preview; preview again before importing. An import whose keys already match does not restart UDM.

The version 1 bundle uses AES-256-CBC encryption with OpenSSL PBKDF2/SHA-256 at 300,000 iterations. A separate salt derives an HMAC-SHA-256 key to authenticate the encrypted envelope before decryption. The passphrase is not retained in appliance configuration or command arguments. Short-lived request files are private and removed after the operation.

## Delete and generate

**Use existing keys** lists the configured keys and provides a delete control. Deletion requires confirmation and removes the UDM reference, the managed private key when no other entry references it, and the associated public exports. Deleting the final key is allowed, but SIMs/eSIMs that use it will no longer have a corresponding concealment key on that core.

Generation adds a new key ID. Generation, import and deletion use the same transaction: back up, validate, update UDM atomically, refresh public exports, and restart UDM only if it was already running. A failed restart restores the prior configuration and attempts to restore the prior running state.

Private keys and `udm.yaml` are archived before changes under `/root/opncell-hnet-recovery/`, with a private directory and archive. These archives contain private keys and are intended for administrator recovery, not public distribution.

## Public exports and compatibility

Public PEM and HEX exports live in `/usr/local/etc/open5gs/hnet/public/` and are rebuilt from the current private keys when keys are listed or changed. Profile A uses a 32-byte X25519 public value; Profile B uses the 33-byte compressed P-256 public point. Key type and scheme must agree.

Changing a core does not update SIM/eSIM provisioning. The public key, protection scheme and key ID provisioned on a SIM/eSIM must match a private key configured on every core expected to serve it.
