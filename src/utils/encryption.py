from Crypto.Cipher import AES;
import os;

key = os.environ.get("DISCORD_OBFUS_KEY")
if not key:
	raise ValueError("DISCORD_OBFUS_KEY is not set.")
key_b = key.encode();

def encrypt_id(_id: int):
	id_bytes = _id.to_bytes(8, "big") + b"\x00" * 8

	cipher = AES.new(key_b, AES.MODE_ECB);
	encrypted = cipher.encrypt(id_bytes);

	return int.from_bytes(encrypted[:8], 'big', signed=True);

def decrypt_id(encrypted: int):
	partial_block = encrypted.to_bytes(8, 'big', signed=True);
	padded_block = partial_block + b"\x00" * 8;

	cipher = AES.new(key_b, AES.MODE_ECB);
	decrypted = cipher.decrypt(padded_block);

	return int.from_bytes(decrypted[:8], 'big');