# from cryptography.fernet import Fernet
# import base64
# message = "123"

# # encrypt and decrypt key
# key = Fernet.generate_key()

# # Fernet instance
# fernet = Fernet(key)

# encMessage = fernet.encrypt(message.encode())
# simpanEncoded = base64.b64encode(encMessage)
# ambilDecoded = base64.b64decode(simpanEncoded)
# decMessage = fernet.decrypt(ambilDecoded).decode()
# print("Pesan asli: ", format(message))
# print("Pesan encoded-fernet: ", format(encMessage))
# print("Pesan encoded-base64: ", format(simpanEncoded))
# print("Pesan decoded-base64: ", format(ambilDecoded))
# print("Pesan decoded-fernet: ", format(decMessage))

from werkzeug.security import generate_password_hash, check_password_hash
password = "4321"
hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
print(check_password_hash(hashed_password, password))
print(hashed_password)

