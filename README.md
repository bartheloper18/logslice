# logslice

A fast log filtering utility that supports structured and unstructured log formats with time-range queries.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git
cd logslice && pip install .
```

---

## Usage

Filter logs within a specific time range:

```bash
logslice --file app.log --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00"
```

Works with structured (JSON) and unstructured (plaintext) log formats:

```bash
# JSON logs
logslice --file service.log --format json --start "2024-01-15T08:00:00Z"

# Pipe from stdin
cat app.log | logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00"
```

Use in Python directly:

```python
from logslice import slice_logs

results = slice_logs(
    filepath="app.log",
    start="2024-01-15 08:00:00",
    end="2024-01-15 09:00:00"
)

for entry in results:
    print(entry)
```

---

## Features

- ⚡ Fast binary search on large log files
- 📄 Supports JSON and plaintext log formats
- 🕐 Flexible timestamp parsing
- 🔧 Works as a CLI tool or Python library

---

## License

This project is licensed under the [MIT License](LICENSE).