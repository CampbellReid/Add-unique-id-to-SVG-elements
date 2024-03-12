import xml.etree.ElementTree as ET
import uuid
import re
import sys

# Namespace handling for common SVG namespaces
namespaces = {
    'svg': 'http://www.w3.org/2000/svg'
}

def register_namespaces():
    for ns in namespaces.values():
        ET.register_namespace('', ns)

def generate_guid():
    return "thing-" + str(uuid.uuid4())

def update_svg(svg_file_path):
    register_namespaces()
    
    # Load and parse the SVG file
    tree = ET.parse(svg_file_path)
    root = tree.getroot()

    # Generate a new GUID for the SVG element
    svg_id = generate_guid()
    root.set('id', svg_id)
    
    # Update IDs within the SVG and keep track of changes
    id_map = {}
    for element in root.findall('.//*[@id]'):
        old_id = element.get('id')
        new_id = generate_guid()
        id_map[old_id] = new_id
        element.set('id', new_id)
    
    # Update CSS within <style> tags
    for style in root.findall('.//svg:style', namespaces):
        css_text = style.text
        # Update IDs in CSS
        for old_id, new_id in id_map.items():
            css_text = re.sub(r'url\(#' + old_id + r'\)', f'url(#{new_id})', css_text)
        
        # Scope CSS selectors to the SVG ID
        def scope_selector(match):
            selectors = match.group(1).split(',')
            scoped_selectors = [f'#{svg_id} {selector.strip()}' for selector in selectors]
            return ', '.join(scoped_selectors) + match.group(2)
        
        css_text = re.sub(r'([^{]+)(\{[^}]+\})', scope_selector, css_text)
        style.text = css_text

    # Write the updated SVG to a new file
    output_file_path = svg_file_path.replace('.svg', '_updated.svg')
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)

    print(f"Updated SVG saved to {output_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 update.py {local_svg_file}")
    else:
        svg_file_path = sys.argv[1]
        update_svg(svg_file_path)
