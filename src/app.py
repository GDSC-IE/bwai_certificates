import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

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

# Function to add text to image
def add_text_to_image(image_path, text, output_path, initial_font_size=450, box_y_percent=0.76, line_spacing_percent=0.15):
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Create a drawing context
        draw = ImageDraw.Draw(image)
        
        # Get image dimensions
        width, height = image.size
        
        # Define text box dimensions (as percentage of image size)
        box_width = width * 0.55  # 55% of image width
        box_height = height * 0.15  # 30% of image height
        box_x = (width - box_width) // 2
        box_y = height * box_y_percent  # Adjustable by slider
        
        # Draw the box
        draw.rectangle(
            [(box_x, box_y), (box_x + box_width, box_y + box_height)],
            outline="red",
            width=0
        )
        
        # Load font from fonts directory
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "GoogleSans-Regular.ttf")
        
        # Function to wrap text and adjust font size
        def get_wrapped_text(text, font, max_width, max_height, start_font_size):
            # Start with the initial font size from slider
            font_size = start_font_size
            wrapped_lines = []
            
            while font_size > 50:  # Minimum font size
                try:
                    font = ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    print(f"Error loading font: {str(e)}")
                    font = ImageFont.load_default()
                
                # Split text into words
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    # Try adding the word to current line
                    test_line = ' '.join(current_line + [word])
                    if hasattr(font, "getbbox"):
                        bbox = font.getbbox(test_line)
                        line_width = bbox[2] - bbox[0]
                    else:
                        line_width = draw.textsize(test_line, font=font)[0]
                    
                    if line_width <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Check if all lines fit in the height
                total_height = 0
                line_heights = []
                for line in lines:
                    if hasattr(font, "getbbox"):
                        bbox = font.getbbox(line)
                        line_height = bbox[3] - bbox[1]
                    else:
                        line_height = draw.textsize(line, font=font)[1]
                    line_heights.append(line_height)
                    total_height += line_height
                
                # Add spacing between lines based on the spacing percentage
                if len(lines) > 1:
                    total_height += sum(line_heights) * line_spacing_percent * (len(lines) - 1)
                
                if total_height <= max_height:
                    return font, lines, line_heights
                
                # Reduce font size and try again
                font_size -= 10
            
            # If we get here, use the last successful attempt
            return font, lines, line_heights
        
        # Get wrapped text with appropriate font size
        font, wrapped_lines, line_heights = get_wrapped_text(text, None, box_width, box_height, initial_font_size)
        
        # Calculate total text height including spacing
        total_height = sum(line_heights)
        if len(wrapped_lines) > 1:
            total_height += sum(line_heights) * line_spacing_percent * (len(wrapped_lines) - 1)
        
        # Calculate starting y position to center text block vertically in the box
        y_offset = box_y + (box_height - total_height) / 2
        
        # Ensure text stays within the box
        if y_offset < box_y:
            y_offset = box_y
        
        # Draw each line of text
        for i, line in enumerate(wrapped_lines):
            if hasattr(font, "getbbox"):
                bbox = font.getbbox(line)
                line_width = bbox[2] - bbox[0]
            else:
                line_width = draw.textsize(line, font=font)[0]
            
            # Center horizontally in the box
            x = box_x + (box_width - line_width) / 2
            
            # Draw text
            draw.text((x, y_offset), line, font=font, fill="black")
            
            # Move to next line with spacing
            if i < len(wrapped_lines) - 1:
                y_offset += line_heights[i] * (1 + line_spacing_percent)
        
        # Save the modified image
        image.save(output_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error adding text to image: {str(e)}")
        return False

# Main function
def main():
    st.title("Certificate Generator")
    
    # Load data
    df = load_data()
    
    # Create sidebar
    st.sidebar.header("Settings")
    
    # Name selector
    selected_name = st.sidebar.selectbox("Select Your Name", df['name'].tolist())
    
    # Get the type for the selected name
    selected_type = df[df['name'] == selected_name]['type'].iloc[0]
    
    # Text customization sliders
    st.sidebar.header("Text Settings")
    font_size = st.sidebar.slider("Initial Font Size", 100, 800, 450, 10)
    y_position = st.sidebar.slider("Vertical Position (%)", 0.5, 0.9, 0.76, 0.01)
    line_spacing = st.sidebar.slider("Line Spacing (%)", 0.0, 0.5, 0.15, 0.01)
    
    # Certificate preview
    st.header("Your Certificate")
    
    template_path = os.path.join(os.path.dirname(__file__), "template", f"{selected_type}.jpg")
    
    if os.path.exists(template_path):
        # Generate certificate button
        if st.sidebar.button("Generate Certificate"):
            try:
                print(f"Starting certificate generation for {selected_name}")
                
                # Create a temporary file for the modified image
                temp_image_path = os.path.join(os.path.dirname(__file__), "temp_certificate.jpg")
                
                # Add name to the certificate with custom settings
                if add_text_to_image(
                    template_path, 
                    selected_name, 
                    temp_image_path,
                    initial_font_size=font_size,
                    box_y_percent=y_position,
                    line_spacing_percent=line_spacing
                ):
                    # Display the personalized certificate
                    st.image(temp_image_path, caption=f"Certificate for {selected_name}", use_column_width=True)
                    
                    # Add download button
                    with open(temp_image_path, "rb") as file:
                        image_bytes = file.read()
                    
                    st.download_button(
                        label="Download Certificate",
                        data=image_bytes,
                        file_name=f"{selected_name}_{selected_type}_bwai_hackathon_certificate.jpg",
                        mime="image/jpeg"
                    )
                else:
                    st.error("Failed to generate personalized certificate")
                
                # Clean up temporary file
                os.remove(temp_image_path)
                print("Successfully completed certificate generation")
            except Exception as e:
                st.error(f"Error generating certificate: {str(e)}")
                print(f"Detailed error: {str(e)}")
    else:
        st.error(f"Template for {selected_type} not found at {template_path}")

if __name__ == "__main__":
    main() 