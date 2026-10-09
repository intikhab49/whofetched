"""Finish an OpenTimestamps proof once Bitcoin has confirmed it, then check it against a public block explorer.

Does the job of `ots upgrade` + `ots verify` on machines where the `ots` command won't start (Windows).
Free: no wallet, no bitcoin and no Bitcoin node needed. The block's merkle root comes from blockstream.info.
Exit codes: 0 = complete and checked, 2 = still waiting for Bitcoin, 1 = the proof did not check out.
Usage: python tools/ots_upgrade.py <file>.ots
"""
import json
import sys
import urllib.request

from opentimestamps.calendar import CommitmentNotFoundError, RemoteCalendar
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

EXPLORER = "https://blockstream.info/api"


def pending(stamp):
    """Every (sub-timestamp, pending attestation) pair in the proof tree."""
    for att in stamp.attestations:
        if isinstance(att, PendingAttestation):
            yield stamp, att
    for child in stamp.ops.values():
        yield from pending(child)


def bitcoin(stamp):
    return [(msg, att) for msg, att in stamp.all_attestations() if isinstance(att, BitcoinBlockHeaderAttestation)]


def merkle_root(height):
    with urllib.request.urlopen(f"{EXPLORER}/block-height/{height}", timeout=30) as r:
        block_hash = r.read().decode().strip()
    with urllib.request.urlopen(f"{EXPLORER}/block/{block_hash}", timeout=30) as r:
        return json.load(r)["merkle_root"], block_hash


def main(path):
    with open(path, "rb") as fd:
        detached = DetachedTimestampFile.deserialize(StreamDeserializationContext(fd))

    upgraded = False
    if not bitcoin(detached.timestamp):
        for sub, att in list(pending(detached.timestamp)):
            try:
                sub.merge(RemoteCalendar(att.uri).get_timestamp(sub.msg, timeout=30))
                upgraded = True
            except CommitmentNotFoundError:
                pass  # this calendar hasn't reached Bitcoin yet
            except Exception as e:
                print(f"{att.uri}: {e}")

    confirmed = bitcoin(detached.timestamp)
    if not confirmed:
        print("still waiting for Bitcoin; the calendars hold the digest")
        return 2

    for msg, att in confirmed:
        root, block_hash = merkle_root(att.height)
        # Block explorers show the merkle root byte-reversed relative to the proof.
        if msg[::-1].hex() == root:
            if upgraded:
                with open(path, "wb") as out:
                    detached.serialize(StreamSerializationContext(out))
            print(f"confirmed in Bitcoin block {att.height} ({block_hash}); merkle root matches")
            return 0
    print("proof names a Bitcoin block but its merkle root does not match")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
