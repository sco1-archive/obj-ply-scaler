import warnings
from pathlib import Path
from typing import List, NamedTuple

import click
import click_pathlib
from pint import UnitRegistry
from scan_scaler.obj_scaler import parse_obj
from scan_scaler.ply_scaler import parse_ply


# Initialize a Quantity instance from Pint's default list of units and prefixes
# This is used to determine the scaling factor from the input unit of measurement strings
Q_ = UnitRegistry().Quantity


class ScanFileList(NamedTuple):
    """Helper container for filepaths to scans for scaling."""

    obj: List[Path]
    ply: List[Path]

    @property
    def n_scans(self) -> int:
        """Calculate the total number of scans in the container."""
        return len(self.obj) + len(self.ply)


@click.command()
@click.option(
    "--filepath",
    default=".",
    help="Path to scan file or directory of scans to scale. [Default: .]",
    type=click_pathlib.Path(exists=True),
)
@click.option("--in-unit", "-i", default="m", help="Incoming unit of measurement. [Default: m]")
@click.option("--out-unit", "-o", default="mm", help="Outgoing unit of measurement. [Default: mm]")
@click.option(
    "--recurse/--no-recurse",
    "-r",
    default=False,
    help="Recurse through child directories & process all scans. [Default: --no-recurse]",
)
def main_cli(filepath: Path, in_unit: str, out_unit: str, recurse: bool) -> None:
    """CLI glue for obj_scaler & ply_scaler."""
    scale_factor = calc_scale_factor(in_unit, out_unit)
    files_to_scale = find_scans(filepath, recurse)
    print(f"Scaling from '{in_unit}' to '{out_unit}' (Factor: {scale_factor:.3})")
    print(f"Discovered {files_to_scale.n_scans} scan(s)\n")

    for obj_filepath in files_to_scale.obj:
        obj = parse_obj(obj_filepath)
        obj.scale_vertices(scale_factor)
        obj.add_header_comment(out_unit)
        obj.to_file(generate_output_filename(obj_filepath, out_unit))
        print(f"Scaled: {obj_filepath}")

    for ply_filepath in files_to_scale.ply:
        ply = parse_ply(ply_filepath)
        ply.scale_vertices(scale_factor)
        ply.add_header_comment(out_unit)
        ply.to_file(generate_output_filename(ply_filepath, out_unit))
        print(f"Scaled: {ply_filepath}")


def find_scans(filepath: Path, recurse: bool) -> ScanFileList:
    """
    Identify OBJ and PLY scan(s) available for scaling.

    If the `recurse` flag is `True`:
        * If `filepath` is a directory, scans will be identified recursively using rglob
        * If `filepath` is a file, a warning will be issued & no recursion will be performed

    If the `recurse` flag is `False`:
        * If `filepath` is a directory, scans will be itentified from that directory only
        * If `filepath` is a file, only that file will be considered

    Note: To simplify path case-sensitivity considerations for operating systems that are not
    Windows, scan file extensions are assumed to always be lowercase (`".obj"` or `".ply"`).
    """
    scan_files = ScanFileList([], [])

    if filepath.is_file():
        # Single file presented
        if recurse:
            warnings.warn("Ignoring recursion flag for single-file input", UserWarning)

        if filepath.suffix.lower() == ".obj":
            scan_files.obj.append(filepath)
        elif filepath.suffix.lower() == ".ply":
            scan_files.ply.append(filepath)
    else:
        # Directory presented
        if recurse:
            scan_files.obj.extend(filepath.rglob("*.obj"))
            scan_files.ply.extend(filepath.rglob("*.ply"))
        else:
            scan_files.obj.extend(filepath.glob("*.obj"))
            scan_files.ply.extend(filepath.glob("*.ply"))

    return scan_files


def calc_scale_factor(in_unit: str, out_unit: str) -> float:
    """Calculate the scale factor between the two units of measurement provided."""
    return Q_(in_unit).to(out_unit).magnitude


def generate_output_filename(filepath: Path, out_unit: str) -> Path:
    """Append the output unit of measurement to the filename of the provided filepath."""
    new_filename = f"{filepath.stem}_{out_unit}{filepath.suffix}"
    return filepath.with_name(new_filename)


if __name__ == "__main__":
    main_cli()
