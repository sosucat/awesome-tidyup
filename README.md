# awesome-tidyup

A program to extract file info and accessibility score for low-scoring files from exported
Canvas "TidyUp" HTML files and "Accessibility Report" HTML files.

Contents
 - `src/awesome_tidyup/extract_tidyup.py` — extractor script for TidyUp HTML files
 - `src/awesome_tidyup/extract_access_scores.py` — merge script to add access scores
 - `src/awesome_tidyup/run_all.py` — run both extractors in sequence
 - `data/input_tidyup/` — directory for TidyUp HTML exports (default input)
 - `data/input_access/` — directory for access HTML exports (default input)
 - `tidyup_list.csv` — output from extract_tidyup (default output)
 - `access_scores.csv` — merged output with scores (default output)

## Prerequisites
Install `pixi`

Quick installer (recommended for Linux/macOS):

```
curl -fsSL https://pixi.sh/install.sh | sh
```

Or with `wget`:

```
wget -qO- https://pixi.sh/install.sh | sh
```
After installing, restart your shell so the `pixi` binary is on your `PATH`.


## Quick Start
1. Download TidyUp html files under `data/input_tidyup` and name them `<COURSE NUMBER>.html`.\
Note that you need to download the full html as a single file using a tool like [SingleFile](https://github.com/gildas-lormeau/SingleFile).\
Default `save as html` options in most browsers separate a page into multiple files. Our code does not work with such files.
2. Download Accessibility Report Low Score Files html files under `data/input_access` and name them `access_<COURSE NUMBER>_<ID>.html`. Again, download each page as a single html file.\
Example:
    ```css
    awesome-tidyup/
    ├── data/
    │   ├── input_tidyup/
    │   │   ├── CS-6000-O01.html
    │   │   └── CS-7000-O01.html
    │   └── input_access/
    │       ├── access_CS-6000-O01_1.html
    │       ├── access_CS-6000-O01_2.html
    │       ├── access_CS-6000-O01_3.html
    │       ├── access_CS-7000-O01_1.html
    ```
3. Install workspace dependencies:

    ```
    pixi install
    ```

4. Run the extractor

- Run all extractors in sequence (recommended):

    ```powershell
    pixi run python -m src.awesome_tidyup.run_all
    ```

- Run extract_tidyup only (TidyUp to CSV):

    ```powershell
    pixi run python -m src.awesome_tidyup.extract_tidyup
    ```
    or with custom arguments
    ```powershell
    pixi run python -m src.awesome_tidyup.extract_tidyup -i data/input_tidyup -o tidyup_list.csv
    ```

- Run extract_access_scores only (merge with access HTML):
    ```powershell
    pixi run python -m src.awesome_tidyup.extract_access_scores
    ```
    or with custom arguments

    ```powershell
    pixi run python -m src.awesome_tidyup.extract_access_scores -i data/input_access -t tidyup_list.csv -o access_scores.csv
    ```

## Output

The `extract_tidyup` script writes a `tidyup_list.csv` file with the following columns (header row):

| Column | Description |
|---|---|
| `course_number` | Identifier derived from the input HTML filename (file stem). Example: `CS-6000-O01` |
| `filename` | The stored file name |
| `access_restriction` | `none` or `restricted` |
| `used_in` | Where the file is used (page/module) or `Not Used` |
| `last_updated` | Last-modified date reported in the export |
| `size` | Human-readable file size (KB, MB) |

The `extract_access_scores` script merges with access HTML files and writes `access_scores.csv` with the same columns plus:

| Column | Description |
|---|---|
| `file_link` | Direct link to the file in Canvas |
| `used_in_link` | Link to the page/module where the file is used |
| `score` | Score obtained from the access HTML export (e.g., "85%") |

Notes
- The parser includes a fallback for malformed HTML exports and detects Canvas access restrictions by inspecting the `file-lock` span classes.

Links
- Pixi installation docs: https://pixi.prefix.dev/latest/installation/

License & contact

- MIT License — see `LICENSE` file.
- Contact: Sosuke Ichihashi <pengu1n.i843@gmail.com>
