import hashlib, secrets;

def genseed(nbytes=32):
	return secrets.token_hex(nbytes);

def hashseed(seed):
	_hash = hashlib.sha256();
	_hash.update(bytes(seed, "ascii"));
	return _hash.hexdigest();

def genrandom(server_seed: str, client_seed: str, nonce: str):
	combined = f"{client_seed}:{server_seed}:{nonce}"
	rng_hash = hashlib.sha3_256();
	rng_hash.update(combined.encode());
	return rng_hash.hexdigest();