def decrypt_wii_setting(input_file, output_file):
    # Standard Wii setting.txt XOR key
    key = 0x73B5DBFA
    
    with open(input_file, 'rb') as f:
        buf = bytearray(f.read())

    # Only process up to 256 bytes as per the original Wii spec
    # (or use len(buf) if you want the whole file)
    length = min(len(buf), 256)
    
    for i in range(length):
        # XOR with the lowest 8 bits of the current key
        buf[i] ^= (key & 0xff)
        
        # Rotate the 32-bit key left by 1 bit
        # This is the (key << 1) | (key >> 31) logic
        key = ((key << 1) & 0xFFFFFFFF) | (key >> 31)

    with open(output_file, 'wb') as f:
        f.write(buf)

# Usage
decrypt_wii_setting('setting.txt', 'decrypted.txt')
