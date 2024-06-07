import json
import bcrypt


def main():
    """
    This function gets as input the server's password twice then if they are the same both times it saves the hashed password as the server password.
    """
    # The salt used for the hashing
    salt = bcrypt.gensalt()
    # The pepper used for the hashing
    server_pepper = b"$2b$12$"

    while True:
        pass1 = input("Please enter Server password  ")
        pass2 = input("Please enter the password again  ")
        # If passwords are the same
        if pass1 == pass2:
            # Opens the data file
            json_file = open("C:/Networks/Final_Project/users/data.json", 'r+')
            data = json.load(json_file)
            # Saves the password in bytes (hashing only works on bytes) and adds the pepper for additional security
            password_bytes = pass1.encode() + server_pepper
            # Hashes the password
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            # Decodes the hashed password (makes the password a string) because json doesnt accept bytes
            hashed_password = hashed_password.decode()
            # Saves the data in the file
            data["server"] = ({"username": "SERVER", "password": hashed_password, "salt": salt.decode()})
            json_file.seek(0)
            # Updates file
            json.dump(data, json_file, indent=4)
            break
        # If the password are not the same the user must enter both passwords again


if __name__ == '__main__':
    main()
