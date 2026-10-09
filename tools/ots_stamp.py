"""Timestamp a file with OpenTimestamps (writes <file>.ots), the same way `ots stamp` does.

Written because the `ots` CLI fails to start on Windows (python-bitcoinlib's wallet module wants
OpenSSL through ctypes), while stamping itself only needs the core library.
Only a salted SHA-256 digest leaves the machine. Verify later with any OpenTimestamps client:
    ots upgrade SHA256SUMS.ots     # once a Bitcoin block has confirmed it (a few hours)
    ots verify SHA256SUMS.ots
Usage: python tools/ots_stamp.py <file>
"""
import os
import sys

from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.op import OpAppend, OpSHA256
from opentimestamps.core.serialize import StreamSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

CALENDARS = [
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://a.pool.eternitywall.com",
    "https://ots.btc.catallaxy.com",
]


def main(path):
    with open(path, "rb") as fd:
        detached = DetachedTimestampFile.from_fd(OpSHA256(), fd)

    # Salt the digest so calendars learn nothing about the file, as the official client does.
    salted = detached.timestamp.ops.add(OpAppend(os.urandom(16)))
    tip = salted.ops.add(OpSHA256())

    accepted = 0
    for url in CALENDARS:
        try:
            tip.merge(RemoteCalendar(url).submit(tip.msg, timeout=20))
            accepted += 1
            print(f"submitted to {url}")
        except Exception as e:  # one dead calendar is fine; we only need one
            print(f"skipped {url}: {e}")
    if accepted == 0:
        sys.exit("no calendar accepted the digest; nothing written")

    with open(path + ".ots", "wb") as out:
        detached.serialize(StreamSerializationContext(out))
    print(f"wrote {path}.ots ({accepted} calendars, sha256 {detached.file_digest.hex()})")


if __name__ == "__main__":
    main(sys.argv[1])
