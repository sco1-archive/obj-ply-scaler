from pathlib import Path
from typing import List, NamedTuple


class ObjFile(NamedTuple):
    """
    Provide a simple representative container of the contents of an OBJ file.

    `header` and `faces` remain as raw strings since we're only scaling `vertices` and dumping the
    remaining lines back in as-is.
    """

    header: List[str]
    vertices: List[List[float]]  # Represented as a list of [X, Y, Z] floats
    faces: List[str]

    def scale_vertices(self, factor: float = 1000) -> None:
        """Scale all vertices by the provided `factor`."""
        for idx, vertex in enumerate(self.vertices):
            self.vertices[idx] = [(coord * factor) for coord in vertex]

    def to_file(self, out_filepath: Path) -> None:
        """
        Dump the OBJ data back into the desired `out_filepath`.

        NOTE: If `out_filepath` already exists, all existing contents will be overwritten.
        """
        with out_filepath.open(mode="w") as f:
            # Write headers straight back
            f.write("".join(header for header in self.header))

            # Prepend vertices with "v" before dumping back
            f.write("".join(self.vertex_to_string(vertex) for vertex in self.vertices))

            # Write faces straight back
            f.write("".join(face for face in self.faces))

    def add_header_comment(self, header_comment: str) -> None:
        """
        Append the provided `header_comment` to the existing file header.

        OBJ headers are suffixed by "`#`"
        """
        self.header.append(f"# {header_comment}\n")

    @staticmethod
    def vertex_to_string(vertex: List[float]) -> str:
        """
        Convert the provided vertex into its string representation.

        e.g. [1, 2, 3] -> "v 1 2 3\n"
        """
        return f"v {vertex[0]:.5} {vertex[1]:.5} {vertex[2]:.5}\n"


def parse_obj(filepath: Path) -> ObjFile:
    """
    Parse the provided OBJ file into its relevant components (header, vertices, faces).

    The OBJ file is assumed to be of the form:
        # <header line(s)>
        v <vertex line(s)>
        f <face line(s)>
    """
    header = []
    vertices = []
    faces = []
    with filepath.open(mode="r") as f:
        for line in f:
            if line.startswith("#"):
                header.append(line)
            elif line.startswith("v"):
                vertices.append([float(vertex) for vertex in line.split()[1:]])
            elif line.startswith("f"):
                faces.append(line)

    return ObjFile(header, vertices, faces)
