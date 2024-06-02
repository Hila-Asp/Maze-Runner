import json
import bcrypt


def main():
    salt = bcrypt.gensalt()
    server_pepper = b"$2b$12$"

    while True:
        pass1 = input("Please enter Server password  ")
        pass2 = input("Please enter the password again  ")
        if pass1 == pass2:
            json_file = open("C:/Networks/Final_Project/users/data.json", 'r+')
            data = json.load(json_file)
            password_bytes = pass1.encode() + server_pepper  # hashing only works on bytes
            hashed_password = bcrypt.hashpw(password_bytes, salt)  # hashes the password
            hashed_password = hashed_password.decode()  # decodes that the hashed password will not be in bytes, it will be string because json doesn’t accept bytes
            data["server"] = ({"username": "SERVER", "password": hashed_password, "salt": salt.decode()})
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            break


if __name__ == '__main__':
    main()
