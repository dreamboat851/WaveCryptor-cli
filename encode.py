import numpy as np
from scipy.io.wavfile import write
import random
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import argparse

# Frequency map generator
def dynamic_frequency_allocation():
    base_freq = np.random.randint(500, 1000)
    all_frequencies = [base_freq + i * 50 for i in range(76)]
    np.random.shuffle(all_frequencies)

    characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789. ")
    freq_map = {characters[i]: all_frequencies[i] for i in range(len(characters))}
    unused_freqs = all_frequencies[len(characters):]
    return freq_map, unused_freqs

# Create the audio file
def create_composite_wave(message, freq_map, unused_freqs, filename, duration=0.5, sample_rate=44100):
    composite_wave = np.array([], dtype=np.float32)
    for char in message:
        if char in freq_map:
            freq = freq_map[char]
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave_segment = 0.5 * np.sin(2 * np.pi * freq * t)
            composite_wave = np.concatenate((composite_wave, wave_segment))

            if random.random() < nothing_probability and unused_freqs:
                nothing_freq = random.choice(unused_freqs)
                wave_segment = 0.5 * np.sin(2 * np.pi * nothing_freq * t)
                composite_wave = np.concatenate((composite_wave, wave_segment))

    composite_wave = np.int16(composite_wave / np.max(np.abs(composite_wave)) * 32767)
    write(filename, sample_rate, composite_wave)

# Encrypt and save frequency map
def encrypt_frequency_key_file(freq_map, unused_freqs, key_filename, encryption_key):
    key_dict = {"freq_map": freq_map, "unused_freqs": unused_freqs}
    json_data = json.dumps(key_dict).encode('utf-8')

    # Initialize AES cipher
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(b'1234567890123456'), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the data
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_data) + padder.finalize()

    # Encrypt and save
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    with open(key_filename, 'wb') as f:
        f.write(encrypted_data)

# Generate and save encryption key
def write_encryption_key(key_filename):
    encryption_key = os.urandom(16)  # 128-bit encryption key
    encoded_key = base64.b64encode(encryption_key).decode('utf-8')
    with open(key_filename, 'w') as f:
        f.write(encoded_key)
    return encryption_key

# Command line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="WaveCryptor Encoding Script")
    parser.add_argument('--message', type=str, required=True, help="Message to encode")
    parser.add_argument('--nothing_probability', type=float, required=True, help="Probability of adding nothing frequencies")
    args = parser.parse_args()
    return args.message, args.nothing_probability

# Main execution
if __name__ == "__main__":
    message, nothing_probability = parse_arguments()

    # Make sure the message is uppercase as in your original code
    message = message.upper()

    composite_file = "composite_message.wav"
    frequency_key_file = "frequency_key_encrypted.json"
    encryption_key_file = "encryption_key.key"

    # Generate and store frequency map and encryption key
    freq_map, unused_freqs = dynamic_frequency_allocation()
    create_composite_wave(message, freq_map, unused_freqs, composite_file)
    encryption_key = write_encryption_key(encryption_key_file)
    encrypt_frequency_key_file(freq_map, unused_freqs, frequency_key_file, encryption_key)

    print("Files created: composite_message.wav, frequency_key_encrypted.json, encryption_key.key")
