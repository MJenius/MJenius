import sys
import os
from PIL import Image
import numpy as np
import cv2

def main():
    input_path = "Formal Profile Photo.png"
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    print(f"Loading input photo from: {input_path}")
    img = Image.open(input_path)
    
    # Try using rembg
    no_bg = None
    try:
        print("Removing background using rembg...")
        from rembg import remove
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        no_bg = remove(img)
        print("Background removed successfully.")
    except Exception as e:
        print(f"Warning: Background removal failed: {e}")
        print("Proceeding without background removal.")
        
    if no_bg is not None:
        # Composite onto a solid white background
        white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white_bg, no_bg)
        rgb_img = composite.convert('RGB')
    else:
        # Fallback: composite directly or convert to RGB
        if img.mode in ('RGBA', 'LA'):
            white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            composite = Image.alpha_composite(white_bg, img.convert('RGBA'))
            rgb_img = composite.convert('RGB')
        else:
            rgb_img = img.convert('RGB')
            
    # Convert PIL Image to OpenCV format (BGR)
    open_cv_image = np.array(rgb_img)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    
    # Boost local contrast with CLAHE
    print("Boosting contrast using OpenCV CLAHE...")
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    cl = clahe.apply(gray)
    
    # Apply gamma correction to darken midtones (reveals face features in ASCII)
    gamma = 1.3
    cl_normalized = cl / 255.0
    gamma_corrected = np.uint8(np.power(cl_normalized, gamma) * 255)
    
    # Overlay edges to keep facial outlines sharp
    print("Extracting edge map for outline enhancement...")
    edges = cv2.Canny(cl, 40, 110)
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Combine gamma corrected image with edges (edges made black)
    final_img = gamma_corrected.copy()
    final_img[edges > 0] = 0
    
    # Save the output
    output_path = "source-prepped.png"
    cv2.imwrite(output_path, final_img)
    print(f"Prepped photo saved to: {output_path}")

if __name__ == "__main__":
    main()
