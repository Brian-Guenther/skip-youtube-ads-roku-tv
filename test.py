import cv2
import pytesseract

# Load the image
image = cv2.imread("your_image.png")

# Convert the image to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding to enhance the text
binary_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# Invert the image for better contrast (black text on white background)
inverted_image = cv2.bitwise_not(binary_image)

# Denoise the image
denoised_image = cv2.fastNlMeansDenoising(inverted_image, None, 30, 7, 21)

# Use pytesseract to extract the text with custom config
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(denoised_image, config=custom_config)

print("Extracted Text:", text)
