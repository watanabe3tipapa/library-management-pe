# Library Management Tools

ISBN barcode scanner with web interface and Booklog auto-add tool.

## Two Versions Available

### 1. Browser Version (Recommended)

No installation required - works directly in your browser.

**Try it now:**

```
https://watanabe3tipapa.github.io/library-management-pe/
```

Features:
- Scan ISBN barcodes using camera
- Automatic book info fetch (Google Books API)
- Save as CSV
- Works on mobile and desktop

### 2. Python Version

For advanced automation (Booklog auto-add).

```bash
# Install dependencies
uv sync

# Run scanner
uv run python camera_isbn.py
```

Open http://localhost:5005 in your browser.

## Documentation

- Browser version: [USAGE.html](https://watanabe3tipapa.github.io/library-management-pe/USAGE.html)
- Python version: [USAGE.md](USAGE.md)

## License

MIT License - see LICENSE file

## Version

v0.1.0
