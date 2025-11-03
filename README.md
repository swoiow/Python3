# CPython Windows Builder (GitHub Actions)

This repository provides a simple GitHub Actions workflow to build **CPython for Windows (x64)** from the official source tarballs on `python.org`.

You trigger the workflow manually, pass in a version like `3.12.10` or `3.12.12`, and the pipeline will:

1. Download the matching CPython source from `https://www.python.org/ftp/python/…`
2. Build CPython with the official `PCbuild` scripts (Release / x64)
3. Collect the build outputs
4. Pack them into a **highly compressed `.7z`**
5. Upload the `.7z` as an **artifact**
6. Create a **GitHub Release** with the `.7z` attached

---

## Workflow: `Build CPython (Windows)`

The workflow file is located at:

```text
.github/workflows/build-cpython.yml
````

It is triggered manually via `workflow_dispatch` and exposes one input:

* `python_version` – CPython version to build

  * Example: `3.12.10`, `3.12.12`

Internally, this value is used to construct:

* Download URL:
  `https://www.python.org/ftp/python/<python_version>/Python-<python_version>.tgz`
* Source directory:
  `Python-<python_version>`
* Output archive name:
  `cpython-<python_version>-win64.7z`
* Release tag:
  `v<python_version>-win64`

---

## How to Use

1. **Enable GitHub Actions** for this repository (if not already enabled).
2. Go to the **Actions** tab in GitHub.
3. Select **“Build CPython (Windows)”** workflow.
4. Click **“Run workflow”**.
5. In the dialog:

   * Fill in `python_version`, e.g. `3.12.12`.
   * Click **“Run workflow”**.

GitHub Actions will spin up a `windows-latest` runner and:

* Download & extract the source.
* Run:

  * `get_externals.bat`
  * `build.bat -c Release -p x64`
* Copy build outputs from `PCbuild\amd64\` into `output\`.
* Compress `output\` into:
  `cpython-<version>-win64.7z`
* Upload the `.7z` as an artifact.
* Create a Release with:

  * Tag: `v<version>-win64`
  * Name: `CPython <version> for Windows x64`
  * Asset: `cpython-<version>-win64.7z`

---

## Outputs

After a successful run, you will have:

1. **Actions artifact**

   * Name: `cpython-<version>-win64`
   * File: `cpython-<version>-win64.7z`

2. **GitHub Release**

   * Tag: `v<version>-win64`
   * Title: `CPython <version> for Windows x64`
   * Attached asset: `cpython-<version>-win64.7z`

The `.7z` archive contains the built CPython binaries and related files from `PCbuild\amd64\`.

---

## Notes & Limitations

* Target platform: **Windows x64** (`-p x64` in `build.bat`).
* Build type: **Release** (`-c Release`).
* The workflow uses the official CPython Windows build system (`PCbuild`).
* This is not an official distribution; it is intended for:

  * Personal use
  * Testing new patch versions
  * Custom runtimes built from upstream source
