import easyocr
import cv2
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image
from datetime import datetime
from pyspellchecker import SpellChecker

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False, batch_size=16)

# Path to the input image
image_path = r'EasyOcr\NAIDLF00107055\NAIDLB00004720-0004.jpg'

# Generate a unique name for the output PDF
output_pdf_path = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Read the image using OpenCV
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Could not open or read the image file: {image_path}")

# Apply pre-processing filters
image = cv2.GaussianBlur(image, (5, 5), 0)
image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Perform OCR on the image
result = reader.readtext(image)

# Convert OpenCV image (BGR) to PIL image (RGB)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(image)

# Get the dimensions of the image
img_width, img_height = pil_image.size

# Create a BytesIO object to save the PIL image as a byte stream
img_byte_arr = BytesIO()
pil_image.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)  # Move the cursor to the start of the stream

# Create a canvas for the PDF
c = canvas.Canvas(output_pdf_path, pagesize=(img_width, img_height))

# Set the page size to match the image size
c.setPageSize((img_width, img_height))

# Draw the image on the PDF
c.drawImage(ImageReader(BytesIO(img_byte_arr.getvalue())), 0, 0, width=img_width, height=img_height)

# Register a custom font (you can change this to any font you have)
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

# Initialize spell checker
spell = SpellChecker()

# Draw the extracted text on the PDF as an invisible layer
for (bbox, text, prob) in result:
    if prob > 0.5:  # Only include text with high confidence
        top_left = bbox[0]
        bottom_right = bbox[2]
        x = top_left[0]
        y = img_height - top_left[1]  # Invert y-coordinate for PDF
        text_width = bottom_right[0] - top_left[0]
        text_height = bottom_right[1] - top_left[1]
        font_size = text_height  # Use the height of the bounding box as the font size
        c.setFont('Arial', font_size)
        c.setFillColorRGB(0, 0, 0, alpha=0.5)  # Set text color to black with 50% transparency
        text = spell.correction(text)  # Apply spell checking
        c.drawString(x, y - font_size, text)

# Save the PDF
c.save()

print(f"Searchable PDF saved as {output_pdf_path}")