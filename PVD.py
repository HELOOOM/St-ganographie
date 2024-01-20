import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def decimal_to_binary(n, bit_length=8):
    binary_representation = format(n, f'0{bit_length}b')
    return binary_representation

def prepare_message(secret_data):
    if isinstance(secret_data, str):
        # Convert text to binary
        secret_binary = ''.join(format(ord(char), '08b') for char in secret_data)
    elif isinstance(secret_data, np.ndarray):
        # Convert pixel values of the secret image to binary
        secret_binary = [decimal_to_binary(pixel) for row in secret_data for pixel in row]
    else:
        raise ValueError("Invalid type for secret_data. Supported types are str (text) and numpy.ndarray (image).")

    return secret_binary


def calculate_differences(image):
    differences = []

    for i in range(len(image)):
        row_diff = []

        for j in range(0, len(image[i]) - 1, 2):
            diff = abs(image[i][j] - image[i][j + 1])
            row_diff.append(diff)

        differences.append(row_diff)

    return differences


def calculate_d_prime(differences, smoothness_classes, bit_counts, bit_stream):
    d_prime_matrix = []

    for i in range(len(differences)):
        row_d_prime = []
        bit_index = 0

        for j in range(len(differences[i])):
            di = differences[i][j]
            smoothness_class = smoothness_classes[i][j]
            ti = bit_counts[i][j]
            if smoothness_class == 0:
                lj = 0
                uj = 7
            else:
                lj = 2 ** (smoothness_class - 1) * (2 ** 3)
                uj = 2 * lj - 1

            bi_binary = bit_stream[bit_index:bit_index + ti]
            bit_index += ti

            # Check for empty or non-string bi_binary before converting to an integer
            if bi_binary and isinstance(bi_binary, str):
                try:
                    bi = int(bi_binary, 2)
                except ValueError:
                    bi = 0
            else:
                bi = 0

            d_prime = abs(lj + bi)
            row_d_prime.append(d_prime)

        d_prime_matrix.append(row_d_prime)

    return d_prime_matrix

def calculate_m(differences, d_prime_matrix):
    m_matrix = []

    for i in range(len(differences)):
        row_m = []

        for j in range(len(differences[i])):
            di = differences[i][j]
            d_prime = d_prime_matrix[i][j]
            m = abs(d_prime - di)
            row_m.append(m)

        m_matrix.append(row_m)

    return m_matrix

def generate_stego_image(image, m_matrix, differences):
    stego_image = []

    for i in range(len(image)):
        row_stego = []

        for j in range(0, len(image[i]) - 1, 2):
            pi = image[i][j]
            m = int(m_matrix[i][j // 2])  # Convert m to an integer
            di = differences[i][j // 2]

            if di % 2 == 0:
                p_prime_i = pi - np.ceil(m / 2)
                p_prime_i_plus_1 = pi + np.floor(m / 2)
            else:
                p_prime_i = pi + np.ceil(m / 2)
                p_prime_i_plus_1 = pi - np.floor(m / 2)

            row_stego.extend([p_prime_i, p_prime_i_plus_1])

        stego_image.append(row_stego)

    return stego_image


def embed(original_image_path, secret_message, is_image=True):
    # Load original image
    original_image = Image.open(original_image_path).convert('L')
    original_image = np.array(original_image)

    # Prepare secret message
    secret_bits_to_embed = prepare_message(secret_message)

    # Calculate differences, smoothness classes, and bit counts for the original image based on the new bits to embed
    original_differences = calculate_differences(original_image)

    # Dummy values for smoothness_classes and bit_counts as they are not provided in the code
    original_smoothness_classes = np.zeros_like(original_differences)
    original_bit_counts = np.ones_like(original_differences)

    # Calculate d' matrix
    d_prime_matrix = calculate_d_prime(original_differences, original_smoothness_classes, original_bit_counts,
                                       secret_bits_to_embed)

    # Calculate m matrix
    m_matrix = calculate_m(original_differences, d_prime_matrix)

    # Generate stego image
    stego_image = generate_stego_image(original_image, m_matrix, original_differences)

    return stego_image

# Embed secret text
stego_text_image = embed('lena.png', "TRY TO FIND ME")

# Embed secret image
stego_image_image = embed('lena.png', cv2.imread('baboon.png', cv2.IMREAD_GRAYSCALE))

# Create a figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(10, 5))

# Plot stego text image
axs[0].imshow(stego_text_image, cmap='gray')
axs[0].set_title('Stego Image (secret is text) PDV')

# Plot stego image
axs[1].imshow(stego_image_image, cmap='gray')
axs[1].set_title('Stego Image (secret is "baboon") PDV')

# Display the figure
plt.show()


