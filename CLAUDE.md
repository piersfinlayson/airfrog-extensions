# Airfrog Extension Repository

The published Airfrog extensions, served at https://extensions.airfrog.org/.
`airfrog-v2/docs/ac4-design.md` sections 7 and 13 specify the repository.

## Layout

```
manifest.json                          the signed list
manifest.json.minisig                  its minisign signature
NAME/VERSION/extension-meta.json       the extension metadata, as submitted
NAME/VERSION/extension.wasm            the WASM module, as submitted
NAME/VERSION/wamr-WAMR/model-N.bin   the extension image for model N and WAMR version WAMR
```

An extension with a WASM module has an extension image for each Airfrog
model and WAMR version. An extension without one doesn't have
`extension.wasm` and has one extension image, `wamr-0.0.0/model-0.bin`.

## Signed list

`manifest.json` lists every extension and version with the SHA-256 of each
extension image. It is signed with the manifest key, which signs the other
Airfrog manifests. The Airfrog manifest's `extensions_manifest` is its
address.

```json
{
  "type": "extensions",
  "version": 1,
  "extensions": {
    "one-rom": {
      "depublished": false,
      "versions": [
        {
          "metadata": { "...": "extension-meta.json, unchanged" },
          "images": [
            { "model": 0, "wamr": "0.0.0", "url": "https://extensions.airfrog.org/one-rom/0.1.0/wamr-0.0.0/model-0.bin", "size": 812, "sha256": "..." }
          ]
        }
      ]
    }
  }
}
```

- `version` is the list's schema version, 1.
- `versions` is highest first, by semantic version.
- `depublished` marks the whole extension.

## Extension images

An extension image is the file Airfrog stores for one installed extension: a
header, the extension metadata unchanged and the compiled WASM module.
Multi-byte values are little-endian.

| Offset | Size | Field | Description |
|---|---|---|---|
| 0 | 4 | magic | `AFXI` |
| 4 | 2 | model | The Airfrog model the module is compiled for. 0 for an extension without a module |
| 6 | 2 | | Reserved, 0 |
| 8 | 3 | wamr | The WAMR version the module is compiled for: major, minor, patch. 0 for an extension without a module |
| 11 | 1 | | Reserved, 0 |
| 12 | 4 | metadata_offset | Offset of the extension metadata |
| 16 | 4 | metadata_len | |
| 20 | 4 | module_offset | Offset of the compiled WASM module |
| 24 | 4 | module_len | 0 for an extension without a module |
| 28 | variable | name | The extension name: a 2-byte length, then the name |

The extension metadata follows the name. The module follows the metadata
at the next multiple of 4 bytes, after zeros. Without a module, module_offset
is the end of the image.

## Publishing

An author raises an issue with the Extension publication request template
(`.github/ISSUE_TEMPLATE/extension-publish.yml`), following
`CONTRIBUTIONS.md`. The issue contains the source repository, its tag and the
extension package `NAME-VERSION.afx`, zipped. In this directory:

1. Publish the package:

   ```sh
   airfrog-ext publish NAME-VERSION.afx
   ```

   It checks the extension metadata and any WASM module, writes them under
   `NAME/VERSION/` with the module compiled into an extension image for each
   Airfrog model, adds the version to `manifest.json` and deletes
   `manifest.json.minisig`. It also compiles each
   stored `extension.wasm` that doesn't have images for its WAMR version.
   The image addresses are in the directory of `EXTENSIONS_MANIFEST` in
   airfrog-site's `urls.toml`. Set `SITE` to the airfrog-site directory if it
   isn't beside the airfrog-v2 checkout airfrog-ext was built from.

   It compiles with the pinned, patched wamrc, `wamrc` beside `airfrog-ext`
   or the one `AIRFROG_WAMRC` selects. airfrog-v2's `ci/build-wamrc.sh`
   builds it.

2. Sign `manifest.json` with Airfrog's signing server, using the Python
   airfrog-site's `ci/install-python.sh` installs:

   ```sh
   python3 ../airfrog-site/ci/release-extensions.py --repository . --signer https://HOST:8444
   ```

3. Commit and push.

`airfrog-ext publish` fails, and changes nothing, when:

- the extension metadata breaks a rule in `ac4-design.md` section 13
- the WASM module breaks a rule in `ac4-design.md` section 11, or wamrc
  fails to compile it
- the version is already published
- the extension is depublished
- another extension in the list has its UI on the same host name with a
  different author or contact, because Extension's UIs from one website can
  read each other's browser data

## Depublishing

```sh
airfrog-ext depublish NAME
```

marks the extension depublished in `manifest.json`. Sign, commit and push as
for publishing. Installed copies keep working. The Airfrog Extensions tab
displays "Depublished" without Update, and Install extensions doesn't list it.

## Serving

`.github/workflows/pages.yml` publishes the repository, except Markdown files,
to GitHub Pages on each push to `main`.

## Signature check

`.github/workflows/verify.yml` runs on every push and pull request. It fails
when `manifest.json.minisig` isn't a signature of `manifest.json` by the
manifest key, or when an extension image or `extension-meta.json` doesn't
match the list. It reads the manifest key from airfrog-site's copy,
`commissioning/manifest-key.js`, at its address `MANIFEST_KEY_JS` in
airfrog-site's `urls.toml`. Set the repository variable
`AIRFROG_SITE_REPOSITORY` to airfrog-site's GitHub repository, for example
`OWNER/airfrog-site`. On a push it also enables `check-ui.yml`.

## UI address check

`.github/workflows/check-ui.yml` runs every Monday, and from the Actions tab.
It fetches the UI address of every version of each extension that isn't
depublished, and opens an issue for each address that fails, unless an open
issue for that address exists. GitHub disables a scheduled workflow after 60
days without repository activity. Each run, and each push through
`verify.yml`, enables it again.
