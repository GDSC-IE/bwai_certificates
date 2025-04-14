# GDG Hackathon Certificate Generator

A Streamlit app that generates personalized certificates by adding names to templates based on user types.

## Setup

1. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Download Google Sans font and place it in the `src/fonts` directory as `GoogleSans-Regular.ttf`

## Usage

1. Run the Streamlit app:

   ```
   streamlit run src/app.py
   ```

2. Use the sidebar to:
   - Select your certificate type
   - Select your name
   - Click "Generate Certificate" to add your name to the template
3. Download the generated certificate using the download button

## Directory Structure

- `src/app.py` - The main Streamlit application
- `src/data/participants.csv` - CSV file containing names and types
- `src/template/` - Directory containing SVG certificate templates
- `src/fonts/` - Directory for storing fonts
