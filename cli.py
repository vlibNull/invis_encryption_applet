import argparse
import os
import getpass
from src.utils import key_manager
from src.encryption import crypto

def main():
    parser = argparse.ArgumentParser(description="A command-line tool for encryption and decryption.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Encrypt Command ---
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file.")
    encrypt_parser.add_argument("input_file", help="The file to encrypt.")
    encrypt_parser.add_argument("output_file", help="The destination for the encrypted file.")
    encrypt_parser.add_argument("--key", required=True, help="The name of the key to use for encryption.")
    encrypt_parser.add_argument("--delete-original", action="store_true", help="Delete the original file after encryption.")

    # --- Decrypt Command ---
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file.")
    decrypt_parser.add_argument("input_file", help="The file to decrypt.")
    decrypt_parser.add_argument("output_file", help="The destination for the decrypted file.")
    decrypt_parser.add_argument("--key", required=True, help="The name of the key to use for decryption.")
    decrypt_parser.add_argument("--delete-original", action="store_true", help="Delete the original file after decryption.")

    # --- Generate Key Command ---
    gen_key_parser = subparsers.add_parser("generate-key", help="Generate a new encryption key.")
    gen_key_parser.add_argument("key_name", help="The name of the key to generate.")

    # --- List Keys Command ---
    subparsers.add_parser("list-keys", help="List all available keys.")

    # --- Delete Key Command ---
    del_key_parser = subparsers.add_parser("delete-key", help="Delete a key.")
    del_key_parser.add_argument("key_name", help="The name of the key to delete.")

    # --- Export Key Command ---
    export_key_parser = subparsers.add_parser("export-key", help="Export a key to a file.")
    export_key_parser.add_argument("key_name", help="The name of the key to export.")
    export_key_parser.add_argument("output_file", help="The path to save the exported key.")

    # --- Import Key Command ---
    import_key_parser = subparsers.add_parser("import-key", help="Import a key from a file.")
    import_key_parser.add_argument("input_file", help="The path to the exported key file.")
    import_key_parser.add_argument("key_name", help="The name to save the imported key as.")

    args = parser.parse_args()

    if args.command == "encrypt":
        encrypt_file(args.input_file, args.output_file, args.key, args.delete_original)
    elif args.command == "decrypt":
        decrypt_file(args.input_file, args.output_file, args.key, args.delete_original)
    elif args.command == "generate-key":
        generate_key(args.key_name)
    elif args.command == "list-keys":
        list_keys()
    elif args.command == "delete-key":
        delete_key(args.key_name)
    elif args.command == "export-key":
        export_key(args.key_name, args.output_file)
    elif args.command == "import-key":
        import_key(args.input_file, args.key_name)

def encrypt_file(input_path, output_path, key_name, delete_original=False):
    print(f"Encrypting {input_path}...")
    key = key_manager.load_key(key_name)
    if not key:
        print(f"Error: Key '{key_name}' not found.")
        return

    try:
        with open(input_path, 'rb') as f_in:
            plaintext = f_in.read()
        
        encrypted_data = crypto.encrypt(plaintext, key, input_path)
        if not encrypted_data:
            print("Error: Encryption failed.")
            return

        with open(output_path, 'wb') as f_out:
            f_out.write(encrypted_data)

        print(f"Successfully encrypted to {output_path}")

        if delete_original:
            os.remove(input_path)
            print(f"Deleted original file: {input_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except IOError as e:
        print(f"Error reading or writing file: {e}")

def decrypt_file(input_path, output_path, key_name, delete_original=False):
    print(f"Decrypting {input_path}...")
    key = key_manager.load_key(key_name)
    if not key:
        print(f"Error: Key '{key_name}' not found.")
        return

    try:
        with open(input_path, 'rb') as f_in:
            encrypted_data = f_in.read()

        decryption_result = crypto.decrypt(encrypted_data, key)
        if not decryption_result:
            print("Error: Decryption failed. Wrong key or corrupt data.")
            return
            
        decrypted_data, _ = decryption_result

        with open(output_path, 'wb') as f_out:
            f_out.write(decrypted_data)

        print(f"Successfully decrypted to {output_path}")

        if delete_original:
            os.remove(input_path)
            print(f"Deleted original file: {input_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except IOError as e:
        print(f"Error reading or writing file: {e}")

def generate_key(key_name):
    try:
        key_manager.generate_key(key_name)
        print(f"Successfully generated key: '{key_name}'")
    except ValueError as e:
        print(f"Error: {e}")

def list_keys():
    keys = key_manager.list_keys()
    if not keys:
        print("No keys found.")
        return
    print("Available keys:")
    for key in keys:
        print(f"- {key}")

def delete_key(key_name):
    if key_manager.delete_key(key_name):
        print(f"Successfully deleted key: '{key_name}'")
    else:
        print(f"Error: Key '{key_name}' not found.")

def export_key(key_name, output_file):
    password = getpass.getpass("Enter password to protect exported key: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match.")
        return

    encrypted_data = key_manager.export_key(key_name, password)
    if not encrypted_data:
        print(f"Error: Could not export key '{key_name}'.")
        return

    try:
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
        print(f"Successfully exported key '{key_name}' to {output_file}")
    except IOError as e:
        print(f"Error writing to file: {e}")

def import_key(input_file, key_name):
    password = getpass.getpass(f"Enter password for key file {input_file}: ")
    
    try:
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
            
        raw_key = key_manager.import_key(encrypted_data, password)
        if not raw_key:
            print("Error: Could not decrypt key. Wrong password or corrupt file.")
            return
            
        key_manager.save_key(key_name, raw_key)
        print(f"Successfully imported key as '{key_name}'")
        
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except ValueError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    main()
