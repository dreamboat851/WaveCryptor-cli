import numpy as np
import json
import base64
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Decrypt and load frequency map
def decrypt_frequency_key_file(key_filename, encryption_key):
    with open(key_filename, 'rb') as f:
        encrypted_data = f.read()

    # Initialize AES cipher for decryption
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(b'1234567890123456'), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and unpad data
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    json_data = unpadder.update(padded_data) + unpadder.finalize()
    key_data = json.loads(json_data)

    # Parse decrypted data
    freq_map = {int(v): k for k, v in key_data["freq_map"].items()}
    unused_freqs = set(key_data["unused_freqs"])
    return freq_map, unused_freqs

# Load encryption key from file
def load_encryption_key(key_filename):
    with open(key_filename, 'r') as f:
        encoded_key = f.read()
    encryption_key = base64.b64decode(encoded_key)
    return encryption_key

# Detect and decode frequencies
def detect_frequencies(filename, freq_map, unused_freqs, segment_duration=0.5, threshold=0.5):
    sample_rate, audio_data = wavfile.read(filename)
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0

    segment_size = int(segment_duration * sample_rate)
    num_segments = len(audio_data) // segment_size
    detected_message = []

    for i in range(num_segments):
        segment = audio_data[i * segment_size : (i + 1) * segment_size]
        fft_result = fft(segment)
        freqs = fftfreq(len(fft_result), 1 / sample_rate)
        magnitude = np.abs(fft_result)

        peak_freq = freqs[np.argmax(magnitude)]
        peak_magnitude = np.max(magnitude)

        if peak_magnitude > threshold and peak_freq in freq_map:
            detected_character = freq_map[peak_freq]
            detected_message.append((i, detected_character))
            print(f"Segment {i + 1} - Frequency: {peak_freq:.2f} Hz - Character: {detected_character}")
        else:
            print(f"Segment {i + 1} - No valid character detected.")

    detected_message.sort()
    decoded_message = ''.join(char for _, char in detected_message)
    return decoded_message

# Main function to decode the message
def main(wave_file, frequency_key_file, encryption_key_file):
    encryption_key = load_encryption_key(encryption_key_file)
    freq_map, unused_freqs = decrypt_frequency_key_file(frequency_key_file, encryption_key)

    print("Decryption complete. Frequency map loaded.")
    decoded_message = detect_frequencies(wave_file, freq_map, unused_freqs)
    print("Decoded Message:", decoded_message)

# Example usage
if __name__ == "__main__":
    wave_file = "composite_message.wav"
    frequency_key_file = "frequency_key_encrypted.json"
    encryption_key_file = "encryption_key.key"
    main(wave_file, frequency_key_file, encryption_key_file)
