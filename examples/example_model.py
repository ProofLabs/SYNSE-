################################################################################
# Stevens SysML-IDE: Example Model
# 
# Author: Kishore Pochiraju
# Developed with assistance from Claude Haiku 4.5
################################################################################

"""
Example SysML v2 Model Creation and Usage

This example demonstrates how to create, manipulate, and save SysML v2 models
using the parser library.
"""

from sysml_parser import (
    Model, Package, Class, AttributeUsage, PartUsage, PortUsage,
    Requirement, Function, Association, Multiplicity, SysMLWriter, SysMLParser
)


def create_simple_model() -> Model:
    """Create a simple example model of a vehicle system"""
    
    # Create root model
    model = Model(
        identifier="vehicle_system",
        name="Vehicle System Model",
        author="System Engineer",
        description="A simple SysML model demonstrating vehicle architecture",
        version="1.0"
    )
    
    # Create a package for the system
    vehicle_pkg = Package(
        identifier="vehicle_package",
        name="Vehicle Package",
        documentation="Contains vehicle system elements"
    )
    model.add_package(vehicle_pkg)
    
    # Create Vehicle class
    vehicle = Class(
        identifier="Vehicle",
        name="Vehicle",
        documentation="Abstract vehicle class",
        is_abstract=True
    )
    vehicle_pkg.add_member(vehicle)
    
    # Add attributes to Vehicle
    make_attr = AttributeUsage(
        identifier="make",
        name="make",
        feature_type="String",
        documentation="Vehicle manufacturer"
    )
    vehicle.add_feature(make_attr)
    
    model_attr = AttributeUsage(
        identifier="model",
        name="model",
        feature_type="String",
        documentation="Vehicle model name"
    )
    vehicle.add_feature(model_attr)
    
    # Create Engine class
    engine = Class(
        identifier="Engine",
        name="Engine",
        documentation="Vehicle engine component"
    )
    vehicle_pkg.add_member(engine)
    
    # Add engine attributes
    displacement = AttributeUsage(
        identifier="displacement",
        name="displacement",
        feature_type="Real",
        documentation="Engine displacement in liters"
    )
    engine.add_feature(displacement)
    
    power = AttributeUsage(
        identifier="power",
        name="power",
        feature_type="Real",
        documentation="Engine power in horsepower"
    )
    engine.add_feature(power)
    
    # Create Transmission class
    transmission = Class(
        identifier="Transmission",
        name="Transmission",
        documentation="Vehicle transmission system"
    )
    vehicle_pkg.add_member(transmission)
    
    gears = AttributeUsage(
        identifier="gears",
        name="gears",
        feature_type="Integer",
        documentation="Number of gears",
        default_value=5
    )
    transmission.add_feature(gears)
    
    # Create Car class (inherits from Vehicle)
    car = Class(
        identifier="Car",
        name="Car",
        documentation="A passenger vehicle",
        supertypes=["Vehicle"]
    )
    vehicle_pkg.add_member(car)
    
    # Add parts to Car
    engine_part = PartUsage(
        identifier="engine_part",
        name="engine",
        feature_type="Engine",
        documentation="The vehicle's engine",
        multiplicity=Multiplicity(1, 1),
        is_composite=True
    )
    car.add_feature(engine_part)
    
    transmission_part = PartUsage(
        identifier="transmission_part",
        name="transmission",
        feature_type="Transmission",
        documentation="The vehicle's transmission",
        multiplicity=Multiplicity(1, 1),
        is_composite=True
    )
    car.add_feature(transmission_part)
    
    # Add ports to Car
    data_port = PortUsage(
        identifier="can_bus_port",
        name="CAN Bus",
        feature_type="CANInterface",
        documentation="CAN Bus communication port",
        port_direction="inout",
        interfaces=["CANInterface"]
    )
    car.add_feature(data_port)
    
    # Create requirements package
    req_pkg = Package(
        identifier="requirements",
        name="System Requirements"
    )
    model.add_package(req_pkg)
    
    # Add requirements
    req1 = Requirement(
        identifier="SYS_REQ_001",
        name="System shall have engine",
        requirement_id="SYS-001",
        text="The system shall have a functioning engine with at least 100 horsepower",
        satisfied_by=["engine_part"]
    )
    req_pkg.add_member(req1)
    
    req2 = Requirement(
        identifier="SYS_REQ_002",
        name="System shall have transmission",
        requirement_id="SYS-002",
        text="The system shall have a transmission with at least 4 gears",
        satisfied_by=["transmission_part"]
    )
    req_pkg.add_member(req2)
    
    # Create functions package
    func_pkg = Package(
        identifier="functions",
        name="System Functions"
    )
    model.add_package(func_pkg)
    
    # Add function
    accelerate_func = Function(
        identifier="accelerate",
        name="Accelerate",
        documentation="Function to accelerate the vehicle",
        behavior="Increases engine throttle and vehicle speed"
    )
    
    speed_input = AttributeUsage(
        identifier="desired_speed",
        name="desired_speed",
        feature_type="Real",
        documentation="Desired vehicle speed"
    )
    accelerate_func.add_input(speed_input)
    
    actual_speed = AttributeUsage(
        identifier="actual_speed",
        name="actual_speed",
        feature_type="Real",
        documentation="Actual vehicle speed achieved"
    )
    accelerate_func.add_output(actual_speed)
    
    func_pkg.add_member(accelerate_func)
    
    # Create associations
    car_has_engine = Association(
        identifier="car_engine_assoc",
        name="has engine",
        source_type="Car",
        target_type="Engine",
        source_cardinality=Multiplicity(1, 1),
        target_cardinality=Multiplicity(1, 1)
    )
    vehicle_pkg.add_member(car_has_engine)
    
    return model


def main():
    """Main example function"""
    
    print("=" * 60)
    print("SysML v2 Parser - Example Model Creation")
    print("=" * 60)
    
    # Create the model
    print("\n1. Creating example vehicle system model...")
    model = create_simple_model()
    print(f"   Model created: {model.name}")
    print(f"   Author: {model.author}")
    
    # Print model statistics
    print("\n2. Model Statistics:")
    print(f"   Total packages: {len(model.owned_packages)}")
    total_members = sum(len(pkg.members) for pkg in model.owned_packages.values())
    total_members += len(model.members)
    print(f"   Total elements: {total_members}")
    
    # Print model structure
    print("\n3. Model Structure:")
    for pkg_id, pkg in model.owned_packages.items():
        print(f"   └─ Package: {pkg.name}")
        for member_id, member in pkg.members.items():
            member_type = member.__class__.__name__
            print(f"      ├─ {member_type}: {member.name}")
            if hasattr(member, 'features'):
                for feature_id, feature in member.features.items():
                    print(f"      │  └─ Feature: {feature.name}")
    
    # Serialize to JSON
    print("\n4. Serializing model to JSON...")
    writer = SysMLWriter(model)
    json_output = "/Users/kishore/Projects/SYSML_V2_IDE/examples/vehicle_model.json"
    writer.write_file(json_output, format="json")
    print(f"   Saved to: {json_output}")
    
    # Serialize to XML
    print("\n5. Serializing model to XML...")
    xml_output = "/Users/kishore/Projects/SYSML_V2_IDE/examples/vehicle_model.xml"
    writer.write_file(xml_output, format="xml")
    print(f"   Saved to: {xml_output}")
    
    # Parse back from JSON
    print("\n6. Parsing model back from JSON...")
    parser = SysMLParser()
    parsed_model = parser.parse_file(json_output)
    print(f"   Parsed model: {parsed_model.name}")
    print(f"   Elements parsed: {len(parser.get_all_elements())}")
    
    # Get elements by type
    print("\n7. Querying model elements:")
    classes = parser.get_elements_by_type(Class)
    requirements = parser.get_elements_by_type(Requirement)
    print(f"   Classes: {len(classes)}")
    print(f"   Requirements: {len(requirements)}")
    
    # Print JSON preview
    print("\n8. JSON Output Preview (first 50 lines):")
    print("   " + "=" * 56)
    json_str = writer.to_json_string()
    for i, line in enumerate(json_str.split('\n')[:50]):
        print(f"   {line}")
    if len(json_str.split('\n')) > 50:
        print("   ... (truncated)")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
