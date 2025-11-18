import bcrypt

# Password from database
password_hash = "$2b$12$1tRCTm8YdLH6qND8uaU1QuaczPMpDDj/sFr.phvZf9387HLIxx4/W"

# Test passwords
passwords = ["Admin@123", "admin123", "Admin123", "admin@123"]

for pwd in passwords:
    result = bcrypt.checkpw(pwd.encode('utf-8'), password_hash.encode('utf-8'))
    print(f"Password '{pwd}': {result}")

# Generate a new hash for Admin@123
print("\nGenerating new hash for 'Admin@123':")
new_hash = bcrypt.hashpw("Admin@123".encode('utf-8'), bcrypt.gensalt())
print(f"New hash: {new_hash.decode('utf-8')}")
print(f"Verify: {bcrypt.checkpw('Admin@123'.encode('utf-8'), new_hash)}")
