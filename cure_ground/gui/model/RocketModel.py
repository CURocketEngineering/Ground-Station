import numpy as np
import pyqtgraph.opengl as gl


class RocketModel:
    """
    Smooth shaded rocket model with dynamic lighting for orientation visuals.
    Includes fins, nozzle, and simulated sunlight shading.
    """

    def __init__(self, radius=0.1, body_height=1.0, nose_height=0.3,
                 fin_height=0.15, fin_thickness=0.02, segments=64):
        self.radius = radius
        self.body_height = body_height
        self.nose_height = nose_height
        self.fin_height = fin_height
        self.fin_thickness = fin_thickness
        self.segments = segments

        vertices, faces, base_colors = self._make_geometry()
        self.vertices = vertices
        self.faces = faces
        self.base_colors = base_colors.copy()
        self.face_normals = self._compute_face_normals(vertices, faces)

        # Initial mesh
        self.mesh = gl.GLMeshItem(
            vertexes=vertices,
            faces=faces,
            faceColors=base_colors,
            smooth=True,
            drawEdges=False,
            shader="shaded",
            glOptions="opaque"
        )

    # -------------------------------------------------------------
    def _make_geometry(self):
        seg = self.segments
        θ = np.linspace(0, 2 * np.pi, seg, endpoint=False)

        # ---------------- Cylinder Body ----------------
        z_body = np.array([0, self.body_height])
        θ_grid, z_grid = np.meshgrid(θ, z_body)
        x_body = self.radius * np.cos(θ_grid)
        y_body = self.radius * np.sin(θ_grid)
        z_body = z_grid
        body_vertices = np.column_stack((x_body.flatten(), y_body.flatten(), z_body.flatten()))

        faces = []
        for i in range(seg):
            j = (i + 1) % seg
            faces.append([i, j, i + seg])
            faces.append([j, j + seg, i + seg])

        # ---------------- Nose Cone ----------------
        tip = np.array([0, 0, self.body_height + self.nose_height])
        nose_vertices = [tip]
        tip_index = len(body_vertices)
        base_indices = np.arange(seg, 2 * seg)
        for i in range(seg):
            j = (i + 1) % seg
            faces.append([base_indices[i], base_indices[j], tip_index])

        # ---------------- Fins ----------------
        fin_vertices = []
        fin_faces = []
        fin_base_z = 0.05 * self.body_height
        fin_span = self.radius * 1.7
        fin_root = self.radius * 0.9

        for angle in np.linspace(0, 2 * np.pi, 4, endpoint=False):
            ca, sa = np.cos(angle), np.sin(angle)
            base1 = np.array([fin_root * ca, fin_root * sa, fin_base_z])
            base2 = np.array([fin_root * ca, fin_root * sa, fin_base_z + self.fin_height])
            tip1 = np.array([fin_span * ca, fin_span * sa, fin_base_z + self.fin_height * 0.6])
            tip2 = np.array([fin_span * ca, fin_span * sa, fin_base_z])

            offset = np.array([-sa, ca, 0]) * self.fin_thickness / 2
            verts = np.array([
                base1 + offset,
                base2 + offset,
                tip1 + offset,
                tip2 + offset,
                base1 - offset,
                base2 - offset,
                tip1 - offset,
                tip2 - offset
            ])
            start_index = len(body_vertices) + len(nose_vertices) + len(fin_vertices)
            fin_vertices.extend(verts)

            # Box-like fins (12 triangles)
            fin_faces.extend([
                [start_index, start_index + 1, start_index + 2],
                [start_index, start_index + 2, start_index + 3],
                [start_index + 4, start_index + 5, start_index + 6],
                [start_index + 4, start_index + 6, start_index + 7],
                [start_index, start_index + 4, start_index + 5],
                [start_index, start_index + 1, start_index + 5],
                [start_index + 1, start_index + 2, start_index + 6],
                [start_index + 1, start_index + 5, start_index + 6],
                [start_index + 2, start_index + 3, start_index + 7],
                [start_index + 2, start_index + 6, start_index + 7],
                [start_index + 3, start_index + 0, start_index + 4],
                [start_index + 3, start_index + 7, start_index + 4],
            ])

        # ---------------- Nozzle ----------------
        nozzle_height = 0.08
        z_noz = np.array([-nozzle_height, 0])
        θ_grid, z_grid = np.meshgrid(θ, z_noz)
        x_noz = self.radius * 0.9 * np.cos(θ_grid)
        y_noz = self.radius * 0.9 * np.sin(θ_grid)
        z_noz = z_grid
        noz_vertices = np.column_stack((x_noz.flatten(), y_noz.flatten(), z_noz.flatten()))

        noz_faces = []
        base_offset = len(body_vertices) + len(nose_vertices) + len(fin_vertices)
        for i in range(seg):
            j = (i + 1) % seg
            noz_faces.append([base_offset + i, base_offset + j, base_offset + i + seg])
            noz_faces.append([base_offset + j, base_offset + j + seg, base_offset + i + seg])

        # ---------------- Combine All ----------------
        vertices = np.vstack((body_vertices, nose_vertices, fin_vertices, noz_vertices))
        faces.extend(fin_faces)
        faces.extend(noz_faces)
        faces = np.array(faces)

        # ---------------- Base Colors ----------------
        body_color = np.array([0.2, 0.45, 0.95, 1.0])
        nose_color = np.array([0.9, 0.25, 0.2, 1.0])
        nozzle_color = np.array([0.3, 0.3, 0.3, 1.0])
        colors = np.tile(body_color, (len(faces), 1))
        colors[int(0.8 * len(faces)):, :] = nose_color
        colors[-(2 * seg + 48):, :] = nozzle_color

        return vertices, faces, colors

    # -------------------------------------------------------------
    def _compute_face_normals(self, vertices, faces):
        v0 = vertices[faces[:, 0]]
        v1 = vertices[faces[:, 1]]
        v2 = vertices[faces[:, 2]]
        normals = np.cross(v1 - v0, v2 - v0)
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= np.maximum(norms, 1e-9)
        return normals

    def get_mesh(self):
        return self.mesh
