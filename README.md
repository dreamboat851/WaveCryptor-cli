# WaveCryptor-cli
WaveCryptor is an innovative app that securely encodes and encrypts messages into audio files. The app also offers a streamlined decoding process, which reconstructs the original message using the audio file, frequency key, and encryption key.

## How to Run the Script:
python encode.py --message "Hello World!" --nothing_probability 0.4

This will execute the encoding process with the message "Hello World!" and a 40% chance of inserting nothing frequencies.

It will also generate the following files: 

- composite_message.wav
- encryption_key.key
- frequency_key_encrypted.json

Provided that the above files are at the same directory as the decode.py file, you can regenerate the original message by 

python decode.py
