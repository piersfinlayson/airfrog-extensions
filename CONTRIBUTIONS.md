# Extension Contributions

Airfrog hosts extensions written by third-parties at
[extensions.airfrog.org](https://extensions.airfrog.org/manifest.json). This
means they appear in Install extensions in the Airfrog UI, and can be installed
by name with the CLI:

```bash
airfrog extension install --extension third-party-extension
```

The extension source stays in the third-party's own repository, and its UI on
the third-party's own website.

See [DEVELOPING](DEVELOPING.md) to write an extension.

## Contribution Steps

1. Write an extension and test it on the latest released firmware.
2. Include an [`extension-meta.json`](#extension-metajson) file in your
   extension directory.
3. [Build the package](DEVELOPING.md#building-the-package).
4. Commit and push your extension source to a public repository.
5. Tag the commit you built the package from.
6. [Raise an issue](#raising-an-issue) requesting your extension be published.

## extension-meta.json

An extension contribution must include an `extension-meta.json` file in the
extension's directory. Here is an example:

```json
{
  "name": "hello",
  "display_name": "Hello",
  "version": "1.0.0",
  "description": "Displays the target's state",
  "author": "Ada Lovelace",
  "contact": "https://github.com/ada",
  "source": "https://github.com/ada/airfrog-hello",
  "license": "MIT",
  "firmware": [],
  "ui": "https://ada.github.io/airfrog-hello/"
}
```

| Field | Meaning |
| --- | --- |
| `name` | The short name of the extension. 1 to 32 lower case letters, digits and dashes, starting and ending with a letter or digit |
| `display_name` | Short display string, to be displayed in the Extensions tab and as the name of the extension's own tab. May include spaces |
| `version` | A [semantic version](https://semver.org/), for example `1.0.0` |
| `description` | One line description of the extension's purpose |
| `author` | The extension author's name or a handle |
| `contact` | An email address or web address, for example `https://github.com/ada` |
| `source` | The `https://` address of the repository the extension is built from |
| `license` | An [SPDX identifier](https://spdx.org/licenses/), for example `MIT`. Must permit Airfrog to distribute and host the extension |
| `firmware` | The target firmware the extension is for, for example `["ONE_ROM"]`. `[]` for any target. The names are the firmware IDs in the [Airfrog WebSocket Protocol](https://github.com/piersfinlayson/airfrog-v2/blob/HEAD/docs/websocket-protocol.md#target) |
| `build_output` | Optional. Path to the WASM module, relative to the extension directory |
| `ui` | Optional. The `https://` address of the UI |

An extension must have `build_output`, `ui` or both.

All of the above information is included in the manifest hosted publicly at
https://extensions.airfrog.org.

Notes:

- The file must be no larger than 2,048 bytes.

- The metadata of a published version can't be changed. To change it release a
  new version.

- UIs on the same host name can read each other's browser data, so an extension
  is rejected if another author's extension already uses its host name.

## Versioning

To release a new version of your extension, follow the
[raising an issue](#raising-an-issue) process again.

## Raising an Issue

Raise an issue [here](https://github.com/piersfinlayson/airfrog-extensions/issues/new?template=extension-publish.yml).

Include:
- The URL of a public repository holding your extension's source.
- The tag the package was built from.
- The package. GitHub doesn't accept `.afx` attachments, so zip it.

The extension must:
- include the [`extension-meta.json`](#extension-metajson) the package was built
  from.
- have its UI, if it has one, at the `ui` address.
- run on the latest released firmware, unmodified.

## Publishing

The project maintainer will respond to your issue with any questions, and,
assuming your extension submission is accepted, publish your extension. The
WASM module in the package is compiled for each Airfrog model as part of the
publishing process.

## Depublishing and Modifying Extensions

Please [raise an issue](#raising-an-issue) with your request. A depublished
extension continues to work where it is already installed.

## Extension Lifetime

The lifetime of a published extension is tied to the availability of its UI and
source repository. If either become unavailable the extension may be
depublished.

## Disclaimer

The Airfrog maintainer reserves the right to:
- decline an extension submission at their discretion
- depublish any extension at any time, for any reason.

The Airfrog maintainer provides no warranty for third-party extensions. The
extension's license governs any warranties or lack thereof.

In particular, the maintainer performs no review or auditing of third-party
extensions that are published at https://extensions.airfrog.org.
