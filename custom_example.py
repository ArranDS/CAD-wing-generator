"""
Custom Wing Design Example
Demonstrates how to create custom wing configurations
"""

from wing_generator import Wing, STLExporter


def example_1_commercial_transport():
    """
    Design: Commercial transport aircraft wing
    Optimised for fuel efficiency and cruise performance
    """
    print("\n=== Commercial Transport Wing ===")
    
    wing = Wing(
        root_chord=8.5,      # Large root chord for structural efficiency
        tip_chord=2.5,       # Significant taper for weight reduction
        span=35.0,           # Long span for high aspect ratio
        sweep=28.0,          # Moderate sweep for transonic performance
        dihedral=7.0,        # High dihedral for lateral stability
        twist=6.0,           # Significant wash-out for stall margin
        airfoil='2415',      # Supercritical airfoil for cruise efficiency
        num_sections=35      # High resolution for smooth geometry
    )
    
    vertices, faces = wing.get_wing_geometry()
    properties = wing.calculate_properties(vertices)
    
    print(f"  Wing span: {properties['wing_span']:.1f} m")
    print(f"  Wing area: {properties['estimated_area']:.1f} m²")
    print(f"  Aspect ratio: {properties['aspect_ratio']:.2f}")
    print(f"  Sweep angle: {properties['sweep_angle']:.1f}°")
    
    STLExporter.write_stl('wing_transport.stl', vertices, faces)
    print("  ✓ Exported to wing_transport.stl")


def example_2_racing_sailplane():
    """
    Design: High-performance racing sailplane
    Optimised for minimum sink rate and maximum glide ratio
    """
    print("\n=== Racing Sailplane Wing ===")
    
    wing = Wing(
        root_chord=1.2,      # Thin root for weight reduction
        tip_chord=0.3,       # Aggressive taper
        span=18.0,           # Very high aspect ratio
        sweep=0.0,           # Zero sweep for clean aerodynamics
        dihedral=3.5,        # Moderate dihedral for passive stability
        twist=5.0,           # Strong wash-out for efficient operation
        airfoil='2412',      # Classic laminar airfoil
        num_sections=40      # Maximum resolution
    )
    
    vertices, faces = wing.get_wing_geometry()
    properties = wing.calculate_properties(vertices)
    
    print(f"  Wing span: {properties['wing_span']:.1f} m")
    print(f"  Wing area: {properties['estimated_area']:.2f} m²")
    print(f"  Aspect ratio: {properties['aspect_ratio']:.2f}")
    print(f"  → Maximum glide ratio achievable")
    
    STLExporter.write_stl('wing_sailplane_racing.stl', vertices, faces)
    print("  ✓ Exported to wing_sailplane_racing.stl")


def example_3_solar_uav():
    """
    Design: Solar-powered UAV wing
    Optimised for lightweight, high altitude performance
    """
    print("\n=== Solar-Powered UAV Wing ===")
    
    wing = Wing(
        root_chord=1.5,      # Moderate chord for solar panel area
        tip_chord=0.5,       # Light taper for weight control
        span=5.0,            # Compact for portability
        sweep=12.0,          # Light sweep for structural efficiency
        dihedral=4.5,        # Enhanced for stable autonomous flight
        twist=3.0,           # Moderate wash-out for safe envelope
        airfoil='2415',      # Lifting airfoil for high altitude
        num_sections=20      # Balanced resolution
    )
    
    vertices, faces = wing.get_wing_geometry()
    properties = wing.calculate_properties(vertices)
    
    print(f"  Wing span: {properties['wing_span']:.1f} m")
    print(f"  Wing area: {properties['estimated_area']:.2f} m²")
    print(f"  Aspect ratio: {properties['aspect_ratio']:.2f}")
    print(f"  Sweep angle: {properties['sweep_angle']:.1f}°")
    print(f"  → Optimised for thin-air efficiency")
    
    STLExporter.write_stl('wing_solar_uav.stl', vertices, faces)
    print("  Exported to wing_solar_uav.stl")


def example_4_fighter_config():
    """
    Design: High-performance fighter aircraft
    Optimised for agility, speed, and control authority
    """
    print("\n=== Fighter Aircraft Wing ===")
    
    wing = Wing(
        root_chord=4.2,      # Reasonable chord for control surfaces
        tip_chord=1.5,       # Moderate taper
        span=8.0,            # Compact for roll rate
        sweep=45.0,          # Aggressive sweep for transonic/supersonic
        dihedral=0.0,        # No dihedral (uses canards for stability)
        twist=0.0,           # Minimal twist for control response
        airfoil='0012',      # Thin symmetric airfoil
        num_sections=25      # Standard resolution
    )
    
    vertices, faces = wing.get_wing_geometry()
    properties = wing.calculate_properties(vertices)
    
    print(f"  Wing span: {properties['wing_span']:.1f} m")
    print(f"  Wing area: {properties['estimated_area']:.1f} m²")
    print(f"  Aspect ratio: {properties['aspect_ratio']:.2f}")
    print(f"  Sweep angle: {properties['sweep_angle']:.1f}°")
    print(f"  → Optimised for high-speed performance")
    
    STLExporter.write_stl('wing_fighter.stl', vertices, faces)
    print("  Exported to wing_fighter.stl")


def example_5_parameter_sensitivity_study():
    """
    Demonstrate how wing geometry changes with parameters
    """
    print("\n=== Parameter Sensitivity Study ===")
    print("(Varying sweep angle while keeping other parameters constant)\n")
    
    base_params = {
        'root_chord': 2.0,
        'tip_chord': 1.0,
        'span': 8.0,
        'dihedral': 3.0,
        'twist': 2.0,
        'airfoil': '2412',
        'num_sections': 20
    }
    
    sweep_angles = [0, 15, 30, 45]
    
    for sweep in sweep_angles:
        wing = Wing(**base_params, sweep=sweep)
        vertices, faces = wing.get_wing_geometry()
        properties = wing.calculate_properties(vertices)
        
        filename = f'wing_sweep_{sweep:02d}deg.stl'
        STLExporter.write_stl(filename, vertices, faces)
        
        print(f"  Sweep {sweep:2d}° → AR: {properties['aspect_ratio']:.2f}, Area: {properties['estimated_area']:.2f} m² → {filename}")


if __name__ == '__main__':
    print("=" * 60)
    print("  CUSTOM WING DESIGN EXAMPLES")
    print("=" * 60)
    
    example_1_commercial_transport()
    example_2_racing_sailplane()
    example_3_solar_uav()
    example_4_fighter_config()
    example_5_parameter_sensitivity_study()
    
    print("\n" + "=" * 60)
    print("All wing designs generated successfully!")
    print("=" * 60 + "\n")
