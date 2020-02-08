from pathlib import Path
from typing import List, NamedTuple


class PlyFile(NamedTuple):
    """
    Provide a simple representative container of the contents of an Ply file.

    `header` and `faces` remain as raw strings since we're only scaling `vertices` and dumping the
    remaining lines back in as-is.
    """

    header: List[str]
    vertices: List[List[float]]  # Represented as a list of [X, Y, Z, confidence] floats
    faces: List[str]

    def scale_vertices(self, factor: float = 1000) -> None:
        """Scale all vertices by the provided `factor`."""
        for idx, vertex in enumerate(self.vertices):
            # Scale only the components, not the confidence
            confidence = vertex[-1]  # Pull condfidence out so we can tack it back on after scaling
            self.vertices[idx] = [(coord * factor) for coord in vertex[:-1]]
            self.vertices[idx].append(confidence)

    def to_file(self, out_filepath: Path) -> None:
        """
        Dump the PLY data back into the desired `out_filepath`.

        NOTE: If `out_filepath` already exists, all existing contents will be overwritten.
        """
        with out_filepath.open(mode="w") as f:
            # Write headers straight back
            f.write("".join(header for header in self.header))

            # Stringify the vertex before dumping back
            f.write("".join(self.vertex_to_string(vertex) for vertex in self.vertices))

            # Write faces straight back
            f.write("".join(face for face in self.faces))

    def add_header_comment(self, header_comment: str) -> None:
        """
        Append the provided `header_line` to the existing file header.

        PLY header comments are suffixed by `"comment"` and are before the `"end header"` statement.
        """
        # Insert at -1 so we go before the "end header" statement
        self.header.insert(-1, f"comment {header_comment}\n")

    @staticmethod
    def vertex_to_string(vertex: List[float]) -> str:
        """
        Convert the provided vertex into its string representation.

        e.g. [1, 2, 3, 4] -> "1 2 3 4\n"
        """
        return f"{vertex[0]:.5} {vertex[1]:.5} {vertex[2]:.5} {vertex[3]:5}\n"


def parse_ply(filepath: Path) -> PlyFile:
    """
    Parse the provided PLY file into its relevant components (header, vertices, faces).

    The PLY file is assumed to be of the form:
        <header line(s)>
        element vertex <n_vertices>
        <header line(s)>
        end_header
        <vertex line(s)>
        <face line(s)>
    """
    header = []
    vertices = []
    faces = []
    with filepath.open(mode="r") as f:
        in_header = True
        n_vertices = None
        vertex_counter = 1
        for line in f:
            if in_header:
                # Header assumed to span from the beginning of the file until "end_header" is
                # encountered
                if "end_header" in line:
                    in_header = False

                # Check for the line that tells us how many vertices are present
                # e.g. "element vertex 10777"
                if "element vertex" in line:
                    n_vertices = int(line.split()[-1])

                header.append(line)
                continue

            if vertex_counter <= n_vertices:
                # Vertex lines assumed to be X, Y, Z, Confidence, all as float
                vertices.append([float(val) for val in line.split()])
                vertex_counter += 1
            else:
                faces.append(line)

    return PlyFile(header, vertices, faces)
