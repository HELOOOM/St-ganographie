import numpy as np
import cv2
from scipy.fftpack import dct, idct
from PIL import Image
import matplotlib.pyplot as plt

def apply_dct_blocks(image, block_size):
    blocks = image.reshape(image.shape[0] // block_size, block_size,
                           image.shape[1] // block_size, block_size).transpose(0, 2, 1, 3)
    dct_blocks = np.array([dct(dct(b.T, norm='ortho').T, norm='ortho') for b in blocks])
    return dct_blocks

def hide_pixels_dct(block, n_pixels):
    block[0, :n_pixels] = 0
    return block

def apply_idct_blocks(dct_blocks):
    idct_blocks = np.array([idct(idct(b.T, norm='ortho').T, norm='ortho') for b in dct_blocks])
    return idct_blocks.transpose(0, 2, 1, 3).reshape(dct_blocks.shape[0] * dct_blocks.shape[2],
                                                      dct_blocks.shape[1] * dct_blocks.shape[3])

def embed(original_image_path, secret_image, block_size=8):
    # Load the original image
    original_image = Image.open(original_image_path).convert('L')
    original_image = np.array(original_image)
    # Check if the secret is an image or text
    if isinstance(secret_image, np.ndarray):
        # Resize secret image
        secret_image_resized = cv2.resize(secret_image, (original_image.shape[1], original_image.shape[0]))

        # Number of pixels to hide
        n_pixels_to_hide = np.count_nonzero(secret_image_resized == 255)
    else:
        # Convert text to binary
        secret_binary = ''.join(format(ord(char), '08b') for char in secret_image)

        # Number of pixels to hide
        n_pixels_to_hide = len(secret_binary)

    # Apply DCT on each block of the original image
    dct_original_blocks = apply_dct_blocks(original_image, block_size)

    # Hide pixels in DCT domain
    dct_stego_blocks = np.array([hide_pixels_dct(b, n_pixels_to_hide) for b in dct_original_blocks])

    # Apply inverse DCT to obtain stego image
    stego_image = apply_idct_blocks(dct_stego_blocks)

    return stego_image

# Embed secret text
stego_text_image = embed('lena.png', "TRY TO FIND ME")

# Embed secret image
stego_image_image = embed('lena.png', cv2.imread('baboon.png', cv2.IMREAD_GRAYSCALE))

# Create a figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

# Plot stego text image
axs[0].imshow(stego_text_image, cmap='gray')
axs[0].set_title('Stego Image (secret is text) dct')

# Plot stego image
axs[1].imshow(stego_image_image, cmap='gray')
axs[1].set_title('Stego Image (secret is "baboon") dct')

# Display the figure
plt.show()

