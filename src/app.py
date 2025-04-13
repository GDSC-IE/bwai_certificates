import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import xml.etree.ElementTree as ET
import re

# Set page configuration
st.set_page_config(
    page_title="Certificate Generator",
    page_icon="🎓",
    layout="wide"
)

# Load participant data
@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "participants.csv")
    return pd.read_csv(data_path)

# Function to get text dimensions
def get_text_dimensions(text, font):
    # For newer Pillow versions
    if hasattr(font, "getbbox"):
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    # For older Pillow versions
    elif hasattr(ImageDraw.Draw(Image.new("RGB", (1, 1))), "textsize"):
        return ImageDraw.Draw(Image.new("RGB", (1, 1))).textsize(text, font=font)
    # Fallback
    else:
        return len(text) * font.size // 2, font.size

# Function to add text to SVG
def add_text_to_svg(svg_path, text, output_path):
    try:
        print(f"Processing SVG file: {svg_path}")
        
        # Read the SVG content
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        print("Successfully read SVG file")
        
        # Parse the SVG file
        tree = ET.parse(svg_path)
        root = tree.getroot()
        print("Successfully parsed SVG XML")
        
        # Get dimensions from viewBox if available, else use default width/height
        viewbox = root.get('viewBox')
        if viewbox:
            tokens = viewbox.split()
            width = float(tokens[2])
            height = float(tokens[3])
            print(f"Using viewBox dimensions: {width}x{height}")
        else:
            width = float(root.get('width', '1000'))
            height = float(root.get('height', '1000'))
            print(f"Using default dimensions: {width}x{height}")
        
        # Get the absolute path to the font file
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", "GoogleSans-Regular.ttf"))
        print(f"Font path: {font_path}")
        
        # Check if font file exists. If it does, embed the font as a Base64 data URI.
        if os.path.exists(font_path):
            with open(font_path, 'rb') as font_file:
                font_data = font_file.read()
            encoded_font = base64.b64encode(font_data).decode('utf-8')
            font_src = f"data:font/truetype;base64,{encoded_font}"
        else:
            print(f"Warning: Font file not found at {font_path}. Falling back to system font Arial")
            font_src = None
        
        # Create style element with @font-face if font data is available
        style = ET.Element('style')
        if font_src:
            style.text = f"""
            @font-face {{
                font-family: 'Google Sans';
                src: url('{font_src}') format('truetype');
            }}
            """
            print("Created style element with embedded font")
        else:
            # Optionally, you could set a fallback font-family in the SVG style
            style.text = ""
            print("Created empty style element (no custom font embedded)")

        # Insert the style element at the beginning of the SVG so that it's applied.
        root.insert(0, style)
        print("Added style element to SVG")
        
        # Create a text element that uses the custom font (matching the font-family in @font-face)
        text_element = ET.Element('text', {
            'x': str(width / 2),
            'y': str(height * 0.86),
            'text-anchor': 'middle',
            'font-family': 'Google Sans',
            'font-size': '40',
            'font-weight': 'bold',
            'fill': 'black'
        })
        text_element.text = text
        print("Created text element")
        
        # Append the text element to the SVG
        root.append(text_element)
        print("Added text element to SVG")
        
        # Save the modified SVG to the output file
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully saved modified SVG to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")


# Main function
def main():
    st.title("Certificate Generator")
    
    # Load data
    df = load_data()
    
    # Get unique types
    types = df['type'].unique().tolist()
    
    # Create sidebar
    st.sidebar.header("Settings")
    
    # Type selector
    selected_type = st.sidebar.selectbox("Select Certificate Type", types)
    
    # Filter names by type
    filtered_names = df[df['type'] == selected_type]['name'].tolist()
    
    # Name selector
    selected_name = st.sidebar.selectbox("Select Your Name", filtered_names)
    
    # Certificate preview
    st.header("Certificate Preview")
    
    template_path = os.path.join(os.path.dirname(__file__), "template", f"{selected_type}.svg")
    
    if os.path.exists(template_path):
        # Generate certificate button
        if st.sidebar.button("Generate Certificate"):
            try:
                print(f"Starting certificate generation for {selected_name}")
                # Create a temporary file for the modified SVG
                temp_svg_path = os.path.join(os.path.dirname(__file__), "temp_certificate.svg")
                add_text_to_svg(template_path, selected_name, temp_svg_path)
                
                # Display the SVG
                with open(temp_svg_path, 'r') as f:
                    svg_content = f.read()
                    st.image(svg_content, caption=f"Certificate for {selected_name}", use_column_width=True)
                
                # Download button
                with open(temp_svg_path, 'rb') as f:
                    st.download_button(
                        label="Download Certificate",
                        data=f.read(),
                        file_name=f"{selected_name}_{selected_type}_Certificate.svg",
                        mime="image/svg+xml"
                    )
                
                # Clean up temporary file
                os.remove(temp_svg_path)
                print("Successfully completed certificate generation")
            except Exception as e:
                st.error(f"Error generating certificate: {str(e)}")
                print(f"Detailed error: {str(e)}")
        else:
            try:
                # Display template preview
                with open(template_path, 'r') as f:
                    svg_content = f.read()
                    st.image(svg_content, caption=f"{selected_type} Certificate Template", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying template: {str(e)}")
    else:
        st.error(f"Template for {selected_type} not found.")

if __name__ == "__main__":
    main() 