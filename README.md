# LaKey Threshold PRF

Prototype implementation of [LaKey threshold PRF](https://eprint.iacr.org/2023/1254).

## Development

1. Setup [MP-SPDZ](https://github.com/data61/MP-SPDZ).
```bash
# Initialize submodules.
git submodule update --init --recursive
# Build selected components.
make setup mal-shamir-offline.x malicious-shamir-party.x
cd ..
# Setup communication.
MP-SPDZ/Scripts/setup-ssl.sh
```
2. Run LaKey Threshold PRF.
```bash
PROG=lakey2 Scripts/compile-pre-run.sh
```