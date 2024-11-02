import socket
import threading
import pickle
import ssl
import sys
import random
import json
import bcrypt
from models.player import Player
from models.map import Map
import time

READY = False
# If playing with a client in another computer, change to the ip address
SERVER_IP = "www.HilaFinalProject.com"
PORT = 5555
PLAYERS_LIST = []
CLIENTS_LIST = []
MAP = Map()
GAME_MAP = MAP.create_block_list()
MOVE_VELOCITY = 27
SERVER_CERT = "C:/Networks/Final_Project/Server_certificates/server.crt"
SERVER_KEY = "C:/Networks/Final_Project/Server_certificates/server.key"
JSON_FILE_PATH = "C:/Networks/Final_Project/users/data.json"
MAP_DOCUMENT_FILE_PATH = "C:/Networks/Final_Project/map/Maps.txt"
CURRENT_PLAYER = 0
CATCHER_COUNT = 1
TOO_MANY_PLAYERS_ERROR_CODE = 999
# between 2-7
NUMBER_OF_PLAYERS = int(sys.argv[2])
# Represents which one of the players will be the runner
RUNNER_ID = random.randint(0, NUMBER_OF_PLAYERS - 1)
SERVER_PEPPER = b"$2b$12$"
USER_PEPPER = b"#53$35#$"
JOINED_USERS = []
APPLE_LOCATION = (0, 0)
GAME_SCREEN_HEIGHT = 675
GAME_SCREEN_WIDTH = 675
BLOCK_PIXEL_WIDTH = 27
BLOCK_PIXEL_HEIGHT = 27
LOCK = threading.Lock()


def move_player(player_num, player_move):
    """
    This function moves a player and checks for collision
    :param player_num: Id of the player
    :param player_move: What move the player made - "UP", "DOWN", "LEFT", "RIGHT"
    """
    global PLAYERS_LIST
    # adds a step to the player
    PLAYERS_LIST[player_num].steps += 1
    x = PLAYERS_LIST[player_num].x
    y = PLAYERS_LIST[player_num].y
    if player_move == "RIGHT":
        loc = (x + MOVE_VELOCITY, y)
    elif player_move == "LEFT":
        loc = (x - MOVE_VELOCITY, y)
    elif player_move == "UP":
        loc = (x, y - MOVE_VELOCITY)
    else:
        loc = (x, y + MOVE_VELOCITY)

    # List of players locations
    catchers_location_list = []
    runner_loc = ()
    for i, player in enumerate(PLAYERS_LIST):
        if i != len(PLAYERS_LIST) - 1:
            if not player.is_runner:
                catchers_location_list.append((player.x, player.y))
            else:
                runner_loc = (player.x, player.y)

    if loc == APPLE_LOCATION:
        thread = threading.Thread(target=player_ate_apple_timer, args=(player_num,))
        thread.start()
        update_apple_location()
    if loc in GAME_MAP and not PLAYERS_LIST[player_num].ate_apple:
        # If new location is a block player doesnt move
        loc = (x, y)
    elif (player_num == RUNNER_ID and loc in catchers_location_list) \
            or (player_num != RUNNER_ID and loc == runner_loc):
        # Check for collision - Game ends
        f = open(JSON_FILE_PATH, "r+")
        # updates steps and games played
        data = json.load(f)
        for j, p in enumerate(PLAYERS_LIST):
            if j != len(PLAYERS_LIST) - 1:
                for i, user in enumerate(data["users"]):
                    if p.username == user.get("username"):
                        if p.is_runner:
                            # player is the runner
                            data["users"][i]["games played as runner"] += 1
                            data["users"][i]["avg runner steps"] = round(
                                (data["users"][i]["avg runner steps"] + p.steps) / data["users"][i][
                                    "games played as runner"])
                        else:
                            # player is a catcher
                            data["users"][i]["games played as catcher"] += 1
                            data["users"][i]["avg catcher steps"] = round(
                                (data["users"][i]["avg catcher steps"] + p.steps) / data["users"][i][
                                    "games played as catcher"])

                        # sends stats to players
                        dict_stats = data["users"][i].copy()
                        # it copies the dictionary because if it is not a copy the pop() changes user in the JSON file
                        dict_stats.pop("username")
                        dict_stats.pop("password")
                        dict_stats.pop("salt")
                        CLIENTS_LIST[j].send(pickle.dumps(dict_stats))
                        break
        # Points to the beginning of the file
        f.seek(0)
        json.dump(data, f, indent=4)
        f.close()
        # Empty player list represents game over
        PLAYERS_LIST = []
        return
    PLAYERS_LIST[player_num].set_x_y(loc)


def gets_info_from_client(client, username):
    """
    This function gets new location from client and updates the players list and sends everyone the new players list
    :param username: the username of the player that joined
    :param client: The connection to the client
    """
    global GAME_MAP, CURRENT_PLAYER, CATCHER_COUNT, RUNNER_ID
    # when player starts game this will become a number
    player_num = None
    move_apple_thread = None
    while True:
        try:
            move = pickle.loads(client.recv(4096))
        except (socket.error, pickle.PickleError):
            # If client closed with termination - non-graceful
            print(f"{client.getpeername()} terminated")
            if client in CLIENTS_LIST:
                # if client terminates in home screen client is not in the list
                CLIENTS_LIST.remove(client)
            JOINED_USERS.remove(username)
            send_go_to_home()
            CURRENT_PLAYER = 0
            CATCHER_COUNT = 1
            PLAYERS_LIST.clear()
            GAME_MAP = MAP.create_block_list()
            client.close()
            return
        if type(move) == list:
            # The data is the map that the client created
            for i in range(len(move)):
                # map to save
                move[i] = str(move[i])
            block_locations_string = '/'.join(move)
            input_file = open(MAP_DOCUMENT_FILE_PATH, 'a')
            input_file.write(block_locations_string + "\n")
            input_file.close()
        elif move == "start":
            # Player started game
            if CURRENT_PLAYER > NUMBER_OF_PLAYERS - 1:
                # If too many players have entered, return an error code to the newest player
                client.send(pickle.dumps(TOO_MANY_PLAYERS_ERROR_CODE))
            else:
                if CURRENT_PLAYER == RUNNER_ID:
                    player = Player(CURRENT_PLAYER, is_runner=True, catcher_number=-1, username=username)
                else:
                    player = Player(CURRENT_PLAYER, is_runner=False, catcher_number=CATCHER_COUNT, username=username)
                    CATCHER_COUNT += 1
                player_num = CURRENT_PLAYER
                CLIENTS_LIST.append(client)
                # adds player to list
                PLAYERS_LIST.append(player)
                client.send(pickle.dumps(player))
                CURRENT_PLAYER += 1
                if len(CLIENTS_LIST) == NUMBER_OF_PLAYERS:
                    # If all the players joined the game
                    PLAYERS_LIST.append(APPLE_LOCATION)
                    update_apple_location()
                    time.sleep(1)
                    move_apple_thread = threading.Thread(target=apple_thread)
                    move_apple_thread.start()  # starts the apple thread
                    for connection in CLIENTS_LIST:
                        # Sends the client the game map- this represents the start of the game
                        connection.send(pickle.dumps(GAME_MAP))
        elif move == "get":
            # Sends the players list
            client.send(pickle.dumps(PLAYERS_LIST))
        elif move == "clear":
            # Resets the game
            CLIENTS_LIST.clear()
            PLAYERS_LIST.clear()
            CURRENT_PLAYER = 0
            CATCHER_COUNT = 1
            RUNNER_ID = random.randint(0, NUMBER_OF_PLAYERS - 1)
            GAME_MAP = MAP.create_block_list()
        elif move == "exit":
            # If a player exits while playing the game or in the waiting room from closing the window - graceful
            print(f"{client.getpeername()} has exited the game")
            CLIENTS_LIST.remove(client)
            JOINED_USERS.remove(username)
            send_go_to_home()
            CURRENT_PLAYER = 0
            CATCHER_COUNT = 1
            PLAYERS_LIST.clear()
            GAME_MAP = MAP.create_block_list()
            client.close()
            break
        elif move == "leave":
            # If a player exits in the home screen - graceful
            print(f"{client.getpeername()} left")
            client.close()
            JOINED_USERS.remove(username)
            break
        elif move in ("UP", "DOWN", "LEFT", "RIGHT"):
            if len(PLAYERS_LIST) != 0:
                # While the "game over" message presents and the player moves it creates a error.
                # Therefore, i need to check if the game ended before i move the player
                move_player(player_num, move)
            if len(PLAYERS_LIST) != 0:
                # If after the move the game didn't end
                send_players_to_clients()
        # If move is neither of the above then it is wrong and it does not fit the protocol


def send_players_to_clients():
    """
    This function sends the players list to all clients joined
    """
    with LOCK:
        for client in CLIENTS_LIST:
            client.send(pickle.dumps(PLAYERS_LIST))


def send_go_to_home():
    """
    This function sends to all the clients "home".
    The client gets this and presents a message that a client has exited and that they will be sent to the home screen
    """
    for client in CLIENTS_LIST:
        client.send(pickle.dumps("home"))


def update_apple_location():
    global APPLE_LOCATION
    players_loc = []
    for i in range(len(PLAYERS_LIST) - 1):
        players_loc.append((PLAYERS_LIST[i].x, PLAYERS_LIST[i].y))
    x = random.randint(0, GAME_SCREEN_WIDTH - 1) // BLOCK_PIXEL_WIDTH
    y = random.randint(0, GAME_SCREEN_HEIGHT - 1) // BLOCK_PIXEL_HEIGHT
    pos = (x * BLOCK_PIXEL_WIDTH, y * BLOCK_PIXEL_HEIGHT)
    while pos in GAME_MAP or pos in players_loc:
        x = random.randint(0, GAME_SCREEN_WIDTH - 1) // BLOCK_PIXEL_WIDTH
        y = random.randint(0, GAME_SCREEN_HEIGHT - 1) // BLOCK_PIXEL_HEIGHT
        pos = (x * BLOCK_PIXEL_WIDTH, y * BLOCK_PIXEL_HEIGHT)
    APPLE_LOCATION = pos
    PLAYERS_LIST[len(PLAYERS_LIST) - 1] = APPLE_LOCATION


def apple_thread():
    while len(PLAYERS_LIST) != 0:  # when a game ends the player list is empty
        update_apple_location()
        # send_players_to_clients()
        time.sleep(10)


def player_ate_apple_timer(player_num):

    if len(PLAYERS_LIST) != 0:
        PLAYERS_LIST[player_num].ate_apple = True
        time.sleep(5)
        if len(PLAYERS_LIST) != 0:
            PLAYERS_LIST[player_num].ate_apple = False
            loc = (PLAYERS_LIST[player_num].x, PLAYERS_LIST[player_num].y)
            if loc in GAME_MAP:
                remove_player_from_block(player_num)

        # if time stops when player is on a block


def remove_player_from_block(player_num):
    global PLAYERS_LIST
    count = 1
    players_loc = []
    player_loc = (PLAYERS_LIST[player_num].x, PLAYERS_LIST[player_num].y)
    for player in PLAYERS_LIST:
        if player != PLAYERS_LIST[len(PLAYERS_LIST) - 1]:  # if not apple
            x = player.x
            y = player.y
            players_loc.append((x,y))
    while True:
        new_loc = (player_loc[0] + count * BLOCK_PIXEL_WIDTH, player_loc[1])
        if new_loc not in players_loc and new_loc not in GAME_MAP:
            PLAYERS_LIST[player_num].set_x_y(new_loc)
            break
        new_loc = (player_loc[0], player_loc[1]+count*BLOCK_PIXEL_HEIGHT)
        if new_loc not in players_loc and new_loc not in GAME_MAP:
            PLAYERS_LIST[player_num].set_x_y(new_loc)
            break
        new_loc = (player_loc[0], player_loc[1] - count * BLOCK_PIXEL_HEIGHT)
        if new_loc not in players_loc and new_loc not in GAME_MAP:
            PLAYERS_LIST[player_num].set_x_y(new_loc)
            break
        new_loc = (player_loc[0] - count * BLOCK_PIXEL_WIDTH, player_loc[1])
        if new_loc not in players_loc and new_loc not in GAME_MAP:
            PLAYERS_LIST[player_num].set_x_y(new_loc)
            break
        count += 1
    send_players_to_clients()


def check(action, username, password):
    """
    If action is 'register', this function checks if the username exists - if not it creates a new user and adds it to the json file
    If actions is 'login', this function checks if the username exists - if yes it checks the password -
    if the password is right it returns True. If it's wrong it returns False.
    if a client already joined with the same username it returns false/].
    :param action: Login or register
    :param username: The username of the player that wanted to connect
    :param password: The password of the player that wanted to connect
    :return: True if login/registration Successful. False if not
    """
    # hashing only works on bytes
    password_bytes = password.encode() + USER_PEPPER

    json_file = open(JSON_FILE_PATH, 'r+')
    data = json.load(json_file)
    found_user = False
    if action == "register":
        for user in data["users"]:
            # each user is a dictionary
            if user.get("username") == username:
                found_user = True
        if not found_user:
            # new user - register
            salt = bcrypt.gensalt()
            # hashes the password
            hashed_password = bcrypt.hashpw((password_bytes + USER_PEPPER), salt)
            # decodes that the hashed password will not be in bytes, it will be string
            hashed_password = hashed_password.decode()
            data["users"].append({"username": username, "password": hashed_password, "salt": salt.decode(),
                                  "games played as runner": 0, "games played as catcher": 0, "avg catcher steps": 0,
                                  "avg runner steps": 0})
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.close()
            JOINED_USERS.append(username)
            return True
        else:
            return False
    else:
        # action = "login"
        correct_password = False
        for user in data["users"]:
            # each user is a dictionary
            if user.get("username") == username:
                found_user = True
                if user.get("password") == bcrypt.hashpw((password_bytes + USER_PEPPER),
                                                         user.get("salt").encode()).decode():
                    correct_password = True
        json_file.close()
        if not found_user:
            # username doesnt exist
            return False
        elif not correct_password:
            # username exists, not joined already, but wrong password
            return False
        elif username in JOINED_USERS:
            # This user already joined
            return False
        else:
            # valid username and password
            JOINED_USERS.append(username)
            return True


def main():
    """
    This is the main function for the server
    """
    # checks the admin password and the number of players that are in the configurations
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
        if bcrypt.hashpw((sys.argv[1].encode() + SERVER_PEPPER), data["server"]["salt"].encode()).decode() != \
                data["server"]["password"]:
            # admin password is incorrect
            print("admin password isn't correct. change the entered parameter and try again.")
            return
        elif not 2 <= int(sys.argv[2]) <= 7:
            # the number of players isn't in the right range
            print("number of players isn't in the correct range. change the entered parameter and try again.")
            return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # binds the socket
        server.bind((SERVER_IP, PORT))
    except socket.error as e:
        print(f"Binding Server Socket Failed: {e}")
        return
    server.listen(NUMBER_OF_PLAYERS)
    print("Server Started, Waiting For Players...")

    # Loads SSL certificate and key
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)

    while True:
        # accepts connection with client
        client, address = server.accept()
        # Wraps socket to create a secure socket
        secure_connection = context.wrap_socket(client, server_side=True)
        print("New Client Joined: ", address)
        # gets the action (login or register), the username and the password
        action, username, password = pickle.loads(secure_connection.recv(2048))
        logged_in = check(action, username, password)
        try:
            # sends to client if the login/registration was successful
            secure_connection.send(pickle.dumps(logged_in))
        except (socket.error, pickle.PickleError):
            print(f"connection to {address} was closed")
            secure_connection.close()
        if not logged_in:
            secure_connection.close()
            print(f"Connection to {address} closed! Login / Registration Unsuccessful")
        else:
            thread = threading.Thread(target=gets_info_from_client, args=(secure_connection, username))
            thread.start()


if __name__ == '__main__':
    main()
