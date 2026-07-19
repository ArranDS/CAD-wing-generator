"""
Parametric Aircraft Wing Generator
Generates 3D wing geometry with customizable aerodynamic parameters
Exports to STL format for CAD software compatibility

Author: ArranDS
"""

import numpy as np
from scipy.interpolate import interp1d
import struct


class AirfoilProfile:
    """Generate NACA airfoil profile coordinates"""
    
    @staticmethod
    def naca_4digit(naca_code, num_points=50):
        """
        Generate NACA 4 digit airfoil profile
        Args:
            naca_code: string like '2412' (2% camber, 4% position, 12% thickness)
            num_points: resolution of airfoil curve
        Returns:
            numpy array of (x, y) coordinates
        """
        m = int(naca_code[0]) / 100.0
        p = int(naca_code[1]) / 10.0
        t = int(naca_code[2:]) / 100.0
        
        # Generate x coordinates (0 to 1)
        x = np.linspace(0, 1, num_points)
        
        # Initialize y arrays
        y_c = np.zeros_like(x)  # camber line
        dy_c = np.zeros_like(x)  # camber slope
        
        # Camber line calculation
        for i, xi in enumerate(x):
            if xi < p:
                if p > 0:
                    y_c[i] = (m / (p ** 2)) * (2 * p * xi - xi ** 2)
                    dy_c[i] = (2 * m / (p ** 2)) * (p - xi)
            else:
                if (1 - p) > 0:
                    y_c[i] = (m / ((1 - p) ** 2)) * (1 - 2 * p + 2 * p * xi - xi ** 2)
                    dy_c[i] = (2 * m / ((1 - p) ** 2)) * (p - xi)
        
        # Thickness distribution
        y_t = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 
                       + 0.2843 * x ** 3 - 0.1036 * x ** 4)
        
        # Upper and lower surfaces
        theta = np.arctan(dy_c)
        x_u = x - y_t * np.sin(theta)
        y_u = y_c + y_t * np.cos(theta)
        x_l = x + y_t * np.sin(theta)
        y_l = y_c - y_t * np.cos(theta)
        
        # Combine upper and lower (lower surface reversed)
        airfoil = np.vstack([
            np.column_stack([x_u, y_u]),
            np.column_stack([x_l[::-1], y_l[::-1]])
        ])
        
        return airfoil


class Wing:
    """Parametric wing geometry generator"""
    
    def __init__(self, root_chord=2.0, tip_chord=1.0, span=8.0, sweep=0.0, 
                 dihedral=2.0, twist=0.0, airfoil='2412', num_sections=20):
        """
        Initialize wing with parameters
        
        Args:
            root_chord: chord length at root (meters)
            tip_chord: chord length at tip (meters)
            span: half-span length (meters)
            sweep: sweep angle (degrees)
            dihedral: dihedral angle (degrees)
            twist: twist angle at tip (degrees)
            airfoil: NACA 4-digit code
            num_sections: number of cross-sections for wing surface
        """
        self.root_chord = root_chord
        self.tip_chord = tip_chord
        self.span = span
        self.sweep = np.radians(sweep)
        self.dihedral = np.radians(dihedral)
        self.twist = np.radians(twist)
        self.airfoil = airfoil
        self.num_sections = num_sections
        
        # Generate base airfoil profile
        self.profile = AirfoilProfile.naca_4digit(airfoil, num_points=100)
        
    def get_wing_geometry(self):
        """Generate complete wing geometry with closed surfaces"""
        
        # Span positions (y values)
        y_positions = np.linspace(0, self.span, self.num_sections)
        
        all_vertices = []
        all_faces = []
        vertex_count = 0
        
        # Generate cross-sections along span
        for i, y in enumerate(y_positions):
            # Local chord (linear taper)
            chord = self.root_chord + (self.tip_chord - self.root_chord) * (y / self.span)
            
            # Sweep offset
            x_offset = y * np.tan(self.sweep)
            
            # Dihedral offset
            z_offset = y * np.tan(self.dihedral)
            
            # Twist interpolation (linear along span)
            twist_angle = self.twist * (y / self.span)
            
            # Scale and transform airfoil profile
            scaled_profile = self.profile * chord
            
            # Apply twist rotation (around chord line)
            c = np.cos(twist_angle)
            s = np.sin(twist_angle)
            rotated = np.column_stack([
                scaled_profile[:, 0] * c - scaled_profile[:, 1] * s,
                scaled_profile[:, 0] * s + scaled_profile[:, 1] * c
            ])
            
            # Apply 3D transformations
            section_vertices = np.column_stack([
                rotated[:, 0] + x_offset,  # x with sweep
                np.full(len(rotated), y),  # y (span position)
                rotated[:, 1] + z_offset   # z with dihedral
            ])
            
            all_vertices.append(section_vertices)
            n_profile = len(rotated)
            
            # Generate triangular faces between sections (wing skin)
            if i < self.num_sections - 1:
                for j in range(n_profile - 1):
                    # First triangle
                    all_faces.append([
                        vertex_count + j,
                        vertex_count + j + 1,
                        vertex_count + n_profile + j
                    ])
                    # Second triangle
                    all_faces.append([
                        vertex_count + j + 1,
                        vertex_count + n_profile + j + 1,
                        vertex_count + n_profile + j
                    ])
            
            vertex_count += n_profile
        
        # Combine all vertices first
        vertices = np.vstack(all_vertices)
        n_profile = len(self.profile)
        
        # Close root surface (first cross-section) - triangulate airfoil facing inward
        root_start = 0
        for j in range(1, n_profile - 1):
            all_faces.append([root_start, root_start + j + 1, root_start + j])
        
        # Close tip surface (last cross-section) - triangulate airfoil facing outward
        tip_start = (self.num_sections - 1) * n_profile
        for j in range(1, n_profile - 1):
            all_faces.append([tip_start, tip_start + j, tip_start + j + 1])
        
        # Close leading edge (typically at index 0 of airfoil profile)
        le_index = 0
        for i in range(self.num_sections - 1):
            curr_start = i * n_profile
            next_start = (i + 1) * n_profile
            # Create triangle quad connecting LE points
            all_faces.append([curr_start + le_index, next_start + le_index, curr_start + le_index + 1])
            all_faces.append([next_start + le_index, next_start + le_index + 1, curr_start + le_index + 1])
        
        # Close trailing edge (typically at middle/end of airfoil profile)
        te_index = n_profile - 2  # Point before last
        for i in range(self.num_sections - 1):
            curr_start = i * n_profile
            next_start = (i + 1) * n_profile
            # Create triangle quad connecting TE points
            all_faces.append([curr_start + te_index, curr_start + te_index + 1, next_start + te_index])
            all_faces.append([curr_start + te_index + 1, next_start + te_index + 1, next_start + te_index])
        
        return vertices, np.array(all_faces)
    
    def calculate_properties(self, vertices):
        """Calculate wing properties"""
        
        # Aspect ratio
        area = self._estimate_area()
        aspect_ratio = (2 * self.span) ** 2 / area
        
        # Bounds
        x_min, y_min, z_min = vertices.min(axis=0)
        x_max, y_max, z_max = vertices.max(axis=0)
        
        properties = {
            'wing_span': 2 * self.span,
            'root_chord': self.root_chord,
            'tip_chord': self.tip_chord,
            'estimated_area': area,
            'aspect_ratio': aspect_ratio,
            'sweep_angle': np.degrees(self.sweep),
            'dihedral_angle': np.degrees(self.dihedral),
            'twist_angle': np.degrees(self.twist),
            'bounds': {
                'x_range': (x_min, x_max),
                'y_range': (y_min, y_max),
                'z_range': (z_min, z_max)
            }
        }
        
        return properties
    
    def _estimate_area(self):
        """Estimate wing planform area"""
        avg_chord = (self.root_chord + self.tip_chord) / 2
        return avg_chord * 2 * self.span  # 2 * span for both wings


class STLExporter:
    """Export geometry to STL"""
    
    @staticmethod
    def write_stl(filename, vertices, faces):
        """
        Write geometry to ASCII STL file
        
        Args:
            filename: output file path
            vertices: Nx3 array of vertex coordinates
            faces: Mx3 array of triangle face indices
        """
        with open(filename, 'w') as f:
            f.write("solid wing\n")
            
            for face in faces:
                # Get vertices of triangle
                v0 = vertices[face[0]]
                v1 = vertices[face[1]]
                v2 = vertices[face[2]]
                
                # Calculate normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                
                # Write facet
                f.write(f"  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n")
                f.write("    outer loop\n")
                f.write(f"      vertex {v0[0]:.6e} {v0[1]:.6e} {v0[2]:.6e}\n")
                f.write(f"      vertex {v1[0]:.6e} {v1[1]:.6e} {v1[2]:.6e}\n")
                f.write(f"      vertex {v2[0]:.6e} {v2[1]:.6e} {v2[2]:.6e}\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")
            
            f.write("endsolid wing\n")


def main():
    """Generate example wings with different configurations"""
    
    # Configuration 1: High aspect ratio wing (sailplane)
    print("Generating high aspect ratio wing...")
    wing1 = Wing(
        root_chord=1.8,
        tip_chord=0.6,
        span=10.0,
        sweep=0.0,
        dihedral=3.0,
        twist=2.0,
        airfoil='2412',
        num_sections=25
    )
    vertices1, faces1 = wing1.get_wing_geometry()
    props1 = wing1.calculate_properties(vertices1)
    
    print(f"  Wing span: {props1['wing_span']:.2f} m")
    print(f"  Estimated wing area: {props1['estimated_area']:.2f} m²")
    print(f"  Aspect ratio: {props1['aspect_ratio']:.2f}")
    
    STLExporter.write_stl('/mnt/user-data/outputs/wing_sailplane.stl', vertices1, faces1)
    print("  Exported: wing_sailplane.stl\n")
    
    # Configuration 2: Swept wing (fighter)
    print("Generating swept wing...")
    wing2 = Wing(
        root_chord=2.5,
        tip_chord=1.2,
        span=5.0,
        sweep=25.0,
        dihedral=1.5,
        twist=3.0,
        airfoil='0012',
        num_sections=20
    )
    vertices2, faces2 = wing2.get_wing_geometry()
    props2 = wing2.calculate_properties(vertices2)
    
    print(f"  Wing span: {props2['wing_span']:.2f} m")
    print(f"  Estimated wing area: {props2['estimated_area']:.2f} m²")
    print(f"  Aspect ratio: {props2['aspect_ratio']:.2f}")
    print(f"  Sweep angle: {props2['sweep_angle']:.2f}°")
    
    STLExporter.write_stl('/mnt/user-data/outputs/wing_swept.stl', vertices2, faces2)
    print("  Exported: wing_swept.stl\n")
    
    # Configuration 3: UAV wing (custom parameters)
    print("Generating UAV wing...")
    wing3 = Wing(
        root_chord=1.2,
        tip_chord=0.4,
        span=4.0,
        sweep=15.0,
        dihedral=4.0,
        twist=5.0,
        airfoil='2415',
        num_sections=15
    )
    vertices3, faces3 = wing3.get_wing_geometry()
    props3 = wing3.calculate_properties(vertices3)
    
    print(f"  Wing span: {props3['wing_span']:.2f} m")
    print(f"  Estimated wing area: {props3['estimated_area']:.2f} m²")
    print(f"  Aspect ratio: {props3['aspect_ratio']:.2f}")
    
    STLExporter.write_stl('/mnt/user-data/outputs/wing_uav.stl', vertices3, faces3)
    print("  Exported: wing_uav.stl\n")
    
    print("All wings generated successfully!")


if __name__ == '__main__':
    main()
