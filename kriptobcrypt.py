from werkzeug.security import generate_password_hash, check_password_hash

password = "123"
 # Hash password
# hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
hashed_password = "pbkdf2:sha256:600000$kv221vcE$964f9b56b39f38e1356a4df781aeb4f12b348d606c35b8bbc6868b108d37041f"

cek = check_password_hash(hashed_password, password)

print(hashed_password)
print(cek)