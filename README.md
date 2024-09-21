# LaKey Threshold PRF

Prototype implementation of [LaKey threshold PRF](https://eprint.iacr.org/2023/1254).

## Development

1. Checkout with submodules.
```
git clone --recurse-submodules <repository-url>
```
2. Setup MP-SPDZ.
```
(cd MP-SPDZ && make setup)
```
3. Run LaKey Threshold PRF.
```
./Scripts/compile-pre-run.sh
```