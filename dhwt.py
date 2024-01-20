import cv2
import numpy as np
import pywt
from skimage.metrics import peak_signal_noise_ratio
import matplotlib.pyplot as plt

def decimal_to_binary(n, bit_length=8):
    binary_representation = format(n, f'0{bit_length}b')
    return binary_representation

def divide_into_blocks(image):
    height, width = image.shape
    blocks = []
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            block = image[i:i+8, j:j+8]
            blocks.append(block)
    return blocks

def apply_2D_HWT(block):
    coeffs = pywt.dwt2(block, 'haar')
    return coeffs

def calculate_LSB_bits(coeff):
    return int(np.log2(np.max(np.abs(coeff))))

def embed_message(coeff, message_bits):
    lsb_bits = calculate_LSB_bits(coeff)
    message_bits = message_bits[:lsb_bits]
    modified_coeff = np.copy(coeff).astype(int)

    for i in range(min(len(modified_coeff), len(message_bits))):
        modified_coeff[i] = (modified_coeff[i] & ~1) | int(message_bits[i])

    return modified_coeff

def embed_image(coeff, secret_image_blocks):
    modified_coeff = np.copy(coeff)

    # Adjust to handle different sizes of coefficients and secret image blocks
    for i in range(min(len(modified_coeff), len(secret_image_blocks))):
        modified_coeff[i] = secret_image_blocks[i]

    return modified_coeff

def apply_2D_IHDWT(coeffs):
    block = pywt.idwt2(coeffs, 'haar')
    return block

def calculate_PSNR(original, compressed):
    mse = np.mean((original - compressed) ** 2)
    psnr = 20 * np.log10(255 / np.sqrt(mse))
    return psnr

def embed(image_path, secret_data):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    print(f"Type of secret_data received: {type(secret_data)}")  # Add this line for debugging

    if image is None:
        raise FileNotFoundError(f"Unable to load the image from the path: {image_path}")

    if isinstance(secret_data, str):
        # Convert text to binary
        secret_type = 'message'
        secret_binary = ''.join(format(ord(char), '08b') for char in secret_data)
    elif isinstance(secret_data, np.ndarray):
        # Convert pixel values of the secret image to binary
        secret_type = 'image'
        secret_binary = [decimal_to_binary(pixel) for row in secret_data for pixel in row]
    else:
        raise ValueError("Invalid type for secret_data. Supported types are str (text) and numpy.ndarray (image).")

    blocks = divide_into_blocks(image)

    for i, block in enumerate(blocks):
        coeffs = apply_2D_HWT(block)
        coeffs_list = [list(row) for row in coeffs]

        if secret_type == 'message':
            hh_coeff = coeffs_list[1][1]
            modified_hh_coeff = embed_message(hh_coeff, secret_binary)
        elif secret_type == 'image':
            hh_coeff = coeffs_list[1][1]
            modified_hh_coeff = embed_image(hh_coeff, secret_image_blocks[i])

        coeffs_list[1][1] = modified_hh_coeff
        coeffs = tuple(tuple(row) for row in coeffs_list)

        modified_block = apply_2D_IHDWT(coeffs)
        blocks[i] = modified_block

    compressed_image = np.zeros_like(image)
    height, width = image.shape
    k = 0
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            compressed_image[i:i+8, j:j+8] = blocks[k]
            k += 1

    psnr = calculate_PSNR(image, compressed_image)
    print(f"PSNR: {psnr} dB")

    return compressed_image

# Embed secret text
stego_text_image = embed('lena.png', "TRY TO FIND ME")

# Embed secret image
stego_image_image = embed('lena.png', 'baboon.png')

# Create a figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

# Plot stego text image
axs[0].imshow(stego_text_image, cmap='gray')
axs[0].set_title('Stego Image (secret is text) dhwt')

# Plot stego image
axs[1].imshow(stego_image_image, cmap='gray')
axs[1].set_title('Stego Image (secret is "babbon") dhwt')

# Display the figure
plt.show()

