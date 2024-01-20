import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import ImageTk, Image

def decimal_to_binary(n, bit_length=8):
    binary_representation = format(n, f'0{bit_length}b')
    return binary_representation

def embed(image, secret_data):
    #cover_image = np.array(Image.open(image))
    cover_image = Image.fromarray(image)

    if isinstance(secret_data, str):
        # Convert text to binary
        secret_binary = ''.join(format(ord(char), '08b') for char in secret_data)
    elif isinstance(secret_data, np.ndarray):
        # Convert pixel values of the secret image to binary
        secret_binary = [decimal_to_binary(pixel) for row in secret_data for pixel in row]
    else:
        raise ValueError("Invalid type for secret_data. Supported types are str (text) and numpy.ndarray (image).")

    # Flatten the pixel values of the image
    flat_image = [pixel for row in image for pixel in row]

    # Embed binary values into the image
    stego_image = [pixel - (pixel % 2 + int(bit)) for (pixel, bit) in zip(flat_image, secret_binary)]

    # Handle remaining pixels in the image
    rest_of_image = flat_image[-(len(flat_image) - len(secret_binary)):]
    stego_image.extend(rest_of_image)

    # Convert the list back to a matrix
    rows = len(image)
    cols = len(image[0])
    stego_matrix = [stego_image[i:i + cols] for i in range(0, len(stego_image), cols)]
    stego_array = np.array(stego_matrix)
    stego_image_final = cv2.convertScaleAbs(stego_array)

    return stego_image_final

def calculate_mse_psnr(original_img, stego_image):
    mse = np.mean((original_img - stego_image)**2)
    psnr = 10 * np.log10((255**2) / mse)
    print('MSE:', mse, 'PSNR:', psnr)
    return mse, psnr

original_image = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
secret_text = "TRY TO FIND ME"
secret_image = cv2.imread('baboon.png', cv2.IMREAD_GRAYSCALE)

# Embed secret text
stego_text_image = embed(original_image, secret_text)

# Embed secret image
stego_image_image = embed(original_image, secret_image)

# Resize stego_text_image to match the dimensions of the original image
stego_text_image_resized = cv2.resize(stego_text_image, (original_image.shape[1], original_image.shape[0]))
stego_image_image_res = cv2.resize(stego_text_image, (original_image.shape[1], original_image.shape[0]))

# Create a figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

# Plot stego text image
axs[0].imshow(stego_text_image_resized, cmap='gray')
axs[0].set_title('Stego Image (secret is text) LSB')

# Plot stego image
axs[1].imshow(stego_image_image_res, cmap='gray')
axs[1].set_title('Stego Image (secret is "baboon") LSB')

# Display the figure
plt.show()
