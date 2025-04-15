import sys
import time
import hmac
import hashlib

# ========== Encryption/Decryption ==========

def xor_cipher(data, passphrase="42Piscine"):
    return bytearray([b ^ ord(passphrase[i % len(passphrase)]) for i, b in enumerate(data)])

# ========== Validate the Key ==========

def is_valid_hex_key(hex_string):
    hex_string = hex_string.strip().lower()
    return len(hex_string) == 64 and all(c in '0123456789abcdef' for c in hex_string)

# ========== Save Key to File (Encrypted) ==========

def save_key(hex_key):
    encrypted = xor_cipher(bytearray.fromhex(hex_key))
    with open("ft_otp.key", "wb") as f:
        f.write(encrypted)
    print("Key was successfully saved in ft_otp.key.")

# ========== Load Key from File (Decrypt) ==========

def load_key(file_path):
    with open(file_path, "rb") as f:
        encrypted = f.read()
    decrypted = xor_cipher(encrypted)
    return decrypted

# ========== HOTP Implementation ==========

def hotp(key, counter, digits=6):
    counter_bytes = counter.to_bytes(8, byteorder='big')
    hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    truncated = hmac_hash[offset:offset+4]
    code = int.from_bytes(truncated, byteorder='big') & 0x7FFFFFFF
    return str(code % (10 ** digits)).zfill(digits)

# ========== TOTP: HOTP + Time ==========

def totp(key):
    timestep = int(time.time()) // 30
    return hotp(key, timestep)

# ========== Main Program ==========

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  ./ft_otp -g key.hex      (Generate and store key)")
        print("  ./ft_otp -k ft_otp.key   (Generate OTP)")
        sys.exit(1)

    option = sys.argv[1]
    filename = sys.argv[2]

    if option == '-g':
        try:
            with open(filename, 'r') as f:
                key = f.read().strip()
            if not is_valid_hex_key(key):
                print("Error: key must be 64 hexadecimal characters.")
                sys.exit(1)
            save_key(key)
        except FileNotFoundError:
            print("Error: File not found.")
            sys.exit(1)

    elif option == '-k':
        try:
            key_bytes = load_key(filename)
            otp = totp(key_bytes)
            print(otp)
        except Exception as e:
            print("Error: Failed to generate OTP.")
            sys.exit(1)
    else:
        print("Error: Invalid option.")
        sys.exit(1)

if __name__ == "__main__":
    main()
