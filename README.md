# Library Management Tools

ISBN barcode scanner with a web interface and a Booklog auto-add tool.

Quick links

- Live/browser version: https://watanabe3tipapa.github.io/library-management-pe/
- Browser-version documentation: https://watanabe3tipapa.github.io/library-management-pe/USAGE.html
- Python-version documentation: USAGE.md
- License file: LICENSE

Two versions

1) Browser version (recommended)

- No installation required — works directly in your browser.
- Features listed in this repository:
  - Scan ISBN barcodes using camera
  - Automatic book info fetch (Google Books API)
  - Save results as CSV
  - Works on mobile and desktop

Try it now:

```
https://watanabe3tipapa.github.io/library-management-pe/
```

2) Python version (for automation / Booklog auto-add)

- Python-based tools are included in this repository (examples: `camera_isbn.py`, `booklog_auto_add.py`).

Commands shown in this repository:

```bash
# Install dependencies
uv sync

# Run scanner
uv run python camera_isbn.py
```

After running, the repository README indicates the web UI is available at:

```
http://localhost:5005
```

Documentation

- Browser version usage: https://watanabe3tipapa.github.io/library-management-pe/USAGE.html
- Python version usage: USAGE.md

Requirements (as recorded in pyproject.toml)

- Requires Python: >=3.13
- Dependencies recorded in pyproject.toml:
  - numpy >= 2.4.2
  - opencv-python >= 4.13.0.92
  - playwright >= 1.58.0
  - pyzbar >= 0.1.9
  - Pillow >= 11.0.0
  - flask >= 3.0.0

Repository contents (top-level files)

- .DS_Store
- .gitignore
- .python-version
- LICENSE
- README.md
- USAGE.md
- booklog_auto_add.py
- camera_isbn.py
- docs/
- pyproject.toml
- test_booklog.py
- uv.lock

Development / maintenance

- Version: v0.1.0
- Repository description: TEST REPOSITORY（PUBLIC）
- Last recorded update (repository metadata): 2026-03-09T13:20:46Z
- Archived: false

License

This repository indicates the MIT License. See the included LICENSE file for details.
