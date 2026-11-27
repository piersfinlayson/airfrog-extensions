# Developing Extensions

An extension has a [UI](#ui), a [WASM module](#wasm-module) or both. The WASM
module runs on Airfrog whether or not the UI is open.

See [CONTRIBUTIONS](CONTRIBUTIONS.md) to have your extension published.

## UI

The UI is a web page, displayed in a tab of the Airfrog UI. Host it on your own
website at an `https://` address, for example using GitHub Pages.

Use the Airfrog client library to connect to Airfrog:

```js
const manifest = await fetch('https://meta.piers.rocks/airfrog/manifest.json')
    .then(r => r.json());
const { Airfrog } = await import(new URL('v0.1.0/airfrog.js', manifest.js_library));

const airfrog = await Airfrog.connectExtension();
```

- Call `connectExtension()` within 10 seconds of the page loading, or the tab
  displays that the UI failed to load.
- The tab is resized to the height of the page. Don't size the page to the
  window, for example using `100vh`.
- Only these requests from the [Airfrog WebSocket Protocol](https://github.com/piersfinlayson/airfrog-v2/blob/HEAD/docs/websocket-protocol.md)
  are available. Other AIRFROG_CMD commands fail with `NOT_PERMITTED`:
  - CLAIM
  - RELEASE
  - TARGET_CMD
  - IDENTIFY
  - AIRFROG_CMD get commands
  - EXT_CMD to your own extension

To communicate with the WASM module:

```js
const module = airfrog.extension();
const reply = await module.command(new Uint8Array(0), 2000);
module.addEventListener('notify', e => show(e.detail));
```

`command(data, timeoutMs)` returns the module's reply. It fails with
`NOT_RUNNING` if the module isn't running. The `notify` event is fired for each
notification sent by the module.

## WASM Module

Create a C or Rust project using `airfrog-ext`:

```sh
airfrog-ext new NAME --lang c
airfrog-ext new NAME --lang rust
```

Build it using:

- C: `make WASI_SDK=DIR`, where `DIR` is wasi-sdk's directory
- Rust: `cargo build --release`

The new project logs each event. The C API is documented in
`include/airfrog_ext.h` and the Rust API at
[docs.rs](https://docs.rs/airfrog-ext-api). Use `airfrog-ext api` to update a C
project's headers.

A module must:

- use no more than 64 KB of RAM
- have memory that can't grow
- import only from `afx`
- not export `malloc`, `free` or AssemblyScript's allocator functions
- return from each callback within 100 ms. A module that runs longer is
  stopped.

## Building the Package

`airfrog-ext` is in the [airfrog-v2](https://github.com/piersfinlayson/airfrog-v2)
repository. Build it in the `rust` directory:

```sh
cargo build --release -p airfrog-ext
```

A WASM module also requires `wamrc`. Build it in the repository using
`ci/build-wamrc.sh`, then set `AIRFROG_WAMRC` to it or copy it beside
`airfrog-ext`.

Include an [`extension-meta.json`](CONTRIBUTIONS.md#extension-metajson) in your
extension directory, then build the package in that directory:

```sh
airfrog-ext package
```

This writes `NAME-VERSION.afx`.

## Testing

A package is unsigned, so Airfrog installs it only over serial or over the
access point started by holding the recovery button for 3 seconds. Install
it with the CLI over either:

```sh
airfrog extension install --file NAME-VERSION.afx
```

To test a UI before hosting it, set `ui` to a local address, for example
`http://localhost:8000/hello/`. Set it to its `https://` address and build the
package again before contributing it.
