#!/usr/bin/env python3
import hashlib
import sys
import os

CHUNK_SIZE = 0x200
XOR_TABLE_SIZE = 0x20000
SEED = 0xc9acbcc6
SPLIT_SIZE = 418381824

def generate_xor_table():
    seed_bytes = SEED.to_bytes(4, byteorder='big')
    
    initial_hash = hashlib.md5(seed_bytes).digest()
    
    xortable = bytearray(XOR_TABLE_SIZE)
    xortable[0:16] = initial_hash
    
    for index in range(0x2000):
        hash_obj = hashlib.md5()
        hash_obj.update(xortable)
        md5_result = hash_obj.digest()
        
        offset = index * 0x10
        xortable[offset:offset + 16] = md5_result
    
    return bytes(xortable)

def encrypt_decrypt_data(data):
    xor_table = generate_xor_table()
    
    result_data = bytearray(len(data))
    
    block_index = 0
    for offset in range(0, len(data), CHUNK_SIZE):
        chunk = data[offset:offset + CHUNK_SIZE]
        
        xor_key_offset = (block_index & 0xff) * CHUNK_SIZE
        
        for byte_index in range(len(chunk)):
            if xor_key_offset + byte_index < len(xor_table):
                result_data[offset + byte_index] = chunk[byte_index] ^ xor_table[xor_key_offset + byte_index]
            else:
                result_data[offset + byte_index] = chunk[byte_index]
        
        block_index += 1
    
    return bytes(result_data)

if __name__ == "__main__":
    encrypt_mode = False
    input_files = []
    output_file = None
    
    args = sys.argv[1:]
    
    if '--encrypt' in args or '-e' in args:
        encrypt_mode = True
        args = [a for a in args if a not in ['--encrypt', '-e']]
    
    if len(args) >= 1:
        for arg in args:
            if os.path.isfile(arg):
                if encrypt_mode or arg.endswith('.bin'):
                    input_files.append(arg)
            elif os.path.isdir(arg):
                for i in range(100, 103):
                    filename = f"dustx{i}.bin"
                    filepath = os.path.join(arg, filename)
                    if os.path.exists(filepath):
                        input_files.append(filepath)
            elif not os.path.exists(arg) and not os.path.isdir(arg):
                output_file = arg
    else:
        for i in range(100, 103):
            filename = f"dustx{i}.bin"
            if os.path.exists(filename):
                input_files.append(filename)
    
    if not input_files:
        print("Usage: python decrypt.py [--encrypt|-e] [input_files...] [output_file]")
        print("       python decrypt.py [--encrypt|-e] [directory] [output_file]")
        print("\nOptions:")
        print("  --encrypt, -e    Encrypt files (default: decrypt)")
        print("\nExamples:")
        print("  python decrypt.py dustx100.bin dustx101.bin dustx102.bin")
        print("  python decrypt.py --encrypt flash_dump.bin flash_dump_encrypted.bin")
        print("  python decrypt.py -e /path/to/directory output.bin")
        sys.exit(1)
    
    input_files.sort()
    
    mode_str = "encrypt" if encrypt_mode else "decrypt"
    print(f"Mode: {mode_str}")
    
    if encrypt_mode:
        if len(input_files) != 1:
            print("Error: Encryption mode requires exactly one input file")
            sys.exit(1)
        
        input_file = input_files[0]
        print(f"Reading {input_file}...")
        
        with open(input_file, 'rb') as f_in:
            merged_data = f_in.read()
        
        total_size = len(merged_data)
        num_parts = (total_size + SPLIT_SIZE - 1) // SPLIT_SIZE
        
        print(f"File size: {total_size} bytes")
        print(f"Splitting into {num_parts} part(s) of {SPLIT_SIZE} bytes each...")
        
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.dirname(input_file) if os.path.dirname(input_file) else "."
        
        for part_num in range(num_parts):
            start_offset = part_num * SPLIT_SIZE
            end_offset = min(start_offset + SPLIT_SIZE, total_size)
            part_data = merged_data[start_offset:end_offset]
            
            encrypted_part = encrypt_decrypt_data(part_data)
            
            output_filename = f"dustx{100 + part_num}.bin"
            if output_file and part_num == 0:
                output_path = output_file
            else:
                output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(encrypted_part)
            
            print(f"  Part {part_num + 1}/{num_parts}: {len(encrypted_part)} bytes -> {output_path}")
        
        print(f"\nEncrypted and split into {num_parts} file(s)")
    else:
        print(f"Found {len(input_files)} file(s) to decrypt:")
        for f in input_files:
            print(f"  - {f}")
        
        all_processed = bytearray()
        
        for input_file in input_files:
            print(f"Decrypting {input_file}...")
            with open(input_file, 'rb') as f_in:
                input_data = f_in.read()
            
            processed_data = encrypt_decrypt_data(input_data)
            all_processed.extend(processed_data)
            print(f"  Decrypted {len(processed_data)} bytes")
        
        if not output_file:
            output_file = "flash_dump_decrypted.bin"
        
        with open(output_file, 'wb') as f_out:
            f_out.write(all_processed)
        
        print(f"\nConcatenated and decrypted {len(all_processed)} bytes total -> {output_file}")
