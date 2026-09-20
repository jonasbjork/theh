
## macOS, Linux

```console
docker run --rm -it --mount "type=bind,source=$(pwd),target=/workspace" -w /workspace fedora-tools:local python3 build-inventory.py
```

## Windows


```console
docker run --rm -it --mount "type=bind,source=$($PWD.Path),target=/workspace" -w /workspace fedora-tools:local python3 build-inventory.py
```
