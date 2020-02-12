# obj-ply-scaler
Quick scaling of OBJ and PLY files.

## Installation
This project utilizes [`poetry`](https://python-poetry.org/) for dependency & environment management. Clone or download this repository to your local machine and create a new environment:

```bash
$ cd <project_dir>
$ poetry install
```

Though it's recommended to utilize `poetry`, the project may also be installed via `pip`:

```bash
$ cd <project_dir>
$ pip install .
```

Alternatively, prebuilt binaries for each release are provided at https://github.com/sco1/obj-ply-scaler/releases

## Usage
The `obj-py-scaler` CLI can be invoked using Python:
```bash
$ python scaler.py
```

Or, if a prebuilt binary is present, this may be called directly
```bash
$ scaler.exe
```

When an `*.obj` or `*.ply` file is discovered it is parsed & scaled according to the provided incoming & outgoing units of measurement. The outgoing unit of measurement is added as a comment to the scan file's header & appended to the output scan file name. (e.g. `some_scan.ply` becomes `some_scan_mm.ply`)

### Input Parameters
| Parameter                      | Description                                                  | Default           |
|--------------------------------|--------------------------------------------------------------|-------------------|
| `--filepath`                   | Path to scan file or directory of scans to scale<sup>1</sup> | Current Directory |
| `-i,--in-unit`                 | Incoming unit of measurement<sup>2</sup>                     | meters            |
| `-o, --out-unit`               | Outgoing unit of measurement<sup>2</sup>                     | millimeters       |
| `-r, --recurse / --no-recurse` | Recurse through child directories & process all scans.       | `--no-recurse`    |
| `-s, --skip`                   | Optionally skip scaling of either *.PLY or *.OBJ files       | `None`            |

**Notes:**
1. When a directory of scans is provided for scaling, to simplify path case-sensitivity considerations for discovery of scan files on operating systems that are not Windows, file extensions are assumed to always be lowercase (e.g. `.obj` or `.ply`). Other file extension cases will not be discovered for scaling.
2. Unit parsing is provided by [`pint`](https://github.com/hgrecco/pint) ([docs](https://pint.readthedocs.io/en/latest/)). Supported unit definitions can be found [here](https://github.com/hgrecco/pint/blob/master/pint/default_en.txt)

### Examples

```bash
$ python scaler.py --filepath some_path/01234-some_scan.ply
Scaling from 'm' to 'mm' (Factor: 1000.0)
Discovered 1 scan(s)

Scaled: some_path/01234-some_scan.ply
```

```bash
$ python scaler.py --filepath ./scan_files/
Discovered 4 scan(s)
Scaling from 'm' to 'mm' (Factor: 1000.0) ...

Scaled: scan_files/01234-some_scan.obj
Scaled: scan_files/01235-some_scan.obj
Scaled: scan_files/01234-some_scan.ply
Scaled: scan_files/01235-some_scan.ply
```

```bash
$ python scaler.py --filepath ./scan_files/ --skip OBJ
Discovered 2 scan(s)
Scaling from 'm' to 'mm' (Factor: 1000.0) ...

Scaled: scan_files/01234-some_scan.ply
Scaled: scan_files/01235-some_scan.ply
```

```bash
$ python scaler.py --filepath ./scan_files/ -i m -o fermi
Scaling from 'm' to 'fermi' (Factor: 1e+15)
Discovered 4 scan(s)

Scaled: scan_files/01234-some_scan.obj
Scaled: scan_files/01235-some_scan.obj
Scaled: scan_files/01234-some_scan.ply
Scaled: scan_files/01235-some_scan.ply
```
