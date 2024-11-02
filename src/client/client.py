import socket
import threading
import pickle
import ssl
import pygame
import screeninfo
import tkinter
from tkinter import messagebox
from models.pictures import Pictures
from models.button import Button
from models.creator import Creator

SCREEN_WIDTH = 675
SCREEN_HEIGHT = 702
GAME_SCREEN_HEIGHT = 675
BACKGROUND_COLOR = (128, 128, 128)
BACKGROUND_TEXTURE = Pictures().background_scaled
BLOCK_TEXTURE = Pictures().block_scaled
HOME_SCREEN_PLAYERS_PICTURE = Pictures().players_pic_scaled
INSTRUCTIONS_CATCHERS_PICTURE = Pictures().instructions_catchers_scaled
INSTRUCTIONS_RUNNER_PICTURE = Pictures().instructions_runner_scaled
APPLE_IMAGE = Pictures().apple_scaled
FONT_TYPE = "papyrus"
TEXT_COLOR = (40, 40, 40)
SERVER_PORT = 5555
# In the hosts file in the computer, www.HilaFinalProject.com points to the server's IP
SERVER_IP = "www.HilaFinalProject.com"
WAITING = True
EXIT_CODE = 0
# This is the width and height of the character that will be showed in the waiting room
PLAYER_PIC_WIDTH_HEIGHT = 75
CA_CERT = "C:/Networks/Final_Project/CA_certificate/CA.pem"
TOO_MANY_PLAYERS_ERROR_CODE = 999
PLAYER_EXITED_WAITING_CODE = 1
SERVER_TERMINATED_CODE = 2
# A dictionary with info on the screen
MONITOR = screeninfo.get_monitors()[0]
# Will get it later on from the server
PLAYER = None
# Later on, when the player logs in/registers - will become the window (screen) of the game
WINDOW = None
# Later on, when player logs in/registers - will become the socket that the player communicates with
SECURE_SOCKET = None


def redraw_window(players, game_map):
    """
    This function draws the game map
    :param players: List of players
    :param game_map: Map
    """
    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(BACKGROUND_TEXTURE, (0, 0))
    # Draws the blocks on the screen
    for location in game_map:
        WINDOW.blit(BLOCK_TEXTURE, location)
    # Draws the apple on the screen
        WINDOW.blit(APPLE_IMAGE, players[len(players)-1])
    # Draws the players on the screen
    for i in range(len(players)-1):
        players[i].draw(WINDOW)
    font = pygame.font.SysFont(FONT_TYPE, 20)
    if PLAYER.is_runner:
        text = font.render(f"Runner  Steps: {PLAYER.steps}", True, TEXT_COLOR)
    else:
        text = font.render(f"Catcher {PLAYER.catcher_number}  Steps: {PLAYER.steps}", True, TEXT_COLOR)
    # Draws the player kind (runner/ catcher) and the number of steps the player did
    WINDOW.blit(text, ((SCREEN_WIDTH - text.get_width()) / 2, GAME_SCREEN_HEIGHT))
    pygame.display.update()


def get_info_from_server():
    """
    This function handles the data that is being sent from the server
    """
    global WAITING, EXIT_CODE, PLAYER
    try:
        game_map = pickle.loads(SECURE_SOCKET.recv(8192))
    except (pickle.PickleError, socket.error):
        # If the server terminated in the waiting screen
        WAITING = False
        EXIT_CODE = SERVER_TERMINATED_CODE
        return
        # Stops thread. Returns to waiting_screen() out of the while WAITING loop
    if type(game_map) == str and game_map == "home":
        # If exited in the waiting screen
        EXIT_CODE = PLAYER_EXITED_WAITING_CODE
        WAITING = False
        return
        # Stops thread. Returns to waiting_screen() out of the while WAITING loop
    else:
        WAITING = False
    while not WAITING:
        try:
            # If the server terminated while the game was active
            players = pickle.loads(SECURE_SOCKET.recv(4096))
        except (pickle.PickleError, socket.error):
            WAITING = True
            EXIT_CODE = SERVER_TERMINATED_CODE
            return
            # Stops thread. Returns to play() out of the while not WAITING loop

        if type(players) == str and players == "home":
            EXIT_CODE = PLAYER_EXITED_WAITING_CODE
            WAITING = True
            break
        elif type(players) == dict:
            # Game ended the dictionary is the players stats
            font = pygame.font.SysFont(FONT_TYPE, 100)
            text = font.render("Game Over!", True, TEXT_COLOR)
            # Displays "Game Over!"
            WINDOW.blit(text, ((SCREEN_WIDTH - text.get_width()) / 2, (SCREEN_HEIGHT - text.get_height()) / 2))

            font2 = pygame.font.SysFont(FONT_TYPE, 30)
            text2 = font2.render(
                f'games played as runner: {players.get("games played as runner")}  avg runner steps:'
                f' {players.get("avg runner steps")}\n games played as catcher: '
                f'{players.get("games played as catcher")} avg catcher steps: {players.get("avg catcher steps")}\n ',
                True, TEXT_COLOR)
            # Displays the player's stats
            WINDOW.blit(text2, ((SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text2.get_height()) / 2 + 200))

            pygame.display.update()
            pygame.time.delay(5000)
            PLAYER.steps = 0
            WAITING = True
        else:
            # Draws the window again and updates the player
            PLAYER = players[PLAYER.p_index]
            redraw_window(players, game_map)


def play():
    """
    This function gets inputs from the user and sends it to the server
    """
    global WAITING, EXIT_CODE
    SECURE_SOCKET.send(pickle.dumps("get"))
    while not WAITING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Player exited, closes the screen and stops the game
                SECURE_SOCKET.send(pickle.dumps("exit"))
                pygame.quit()
                SECURE_SOCKET.close()
                return
            if event.type == pygame.KEYDOWN:
                # If the client pressed on the keyboard
                if event.key == pygame.K_RIGHT:
                    SECURE_SOCKET.send(pickle.dumps("RIGHT"))
                if event.key == pygame.K_LEFT:
                    SECURE_SOCKET.send(pickle.dumps("LEFT"))
                if event.key == pygame.K_UP:
                    SECURE_SOCKET.send(pickle.dumps("UP"))
                if event.key == pygame.K_DOWN:
                    SECURE_SOCKET.send(pickle.dumps("DOWN"))

    if SERVER_TERMINATED_CODE == EXIT_CODE:
        # The server Terminated- a message is shown and the client is sent back to the start screen
        WINDOW.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(FONT_TYPE, 35)
        text1 = font.render("The Server Terminated The Game", True, TEXT_COLOR)
        text2 = font.render("You Need To Login Again", True, TEXT_COLOR)
        # Displays a message that the server terminated
        WINDOW.blit(text1, ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
        WINDOW.blit(text2, (
            (SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

        pygame.display.update()
        pygame.time.delay(2000)
        SECURE_SOCKET.close()
        pygame.quit()
        EXIT_CODE = 0
        WAITING = True
        main()
    elif EXIT_CODE == PLAYER_EXITED_WAITING_CODE:
        # A player exited the game- a message is shown and the client is sent back to the home screen
        WINDOW.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(FONT_TYPE, 35)
        text1 = font.render("A Player Has Exited The Game!", True, TEXT_COLOR)
        text2 = font.render("You Are Being Sent Back To Home", True, TEXT_COLOR)
        # displays a message that a player has exited the game
        WINDOW.blit(text1, ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
        WINDOW.blit(text2, (
            (SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

        pygame.display.update()
        pygame.time.delay(2000)
        SECURE_SOCKET.send((pickle.dumps("clear")))
        EXIT_CODE = 0
        WAITING = True
        home_screen()
    else:
        # game ended
        SECURE_SOCKET.send((pickle.dumps("clear")))
        # Returns to main screen if another player exited the game
        home_screen()


def waiting_screen():
    """
    This function displays the waiting for players screen
    """
    global PLAYER, WAITING, EXIT_CODE
    pygame.display.set_caption(PLAYER.username)
    while WAITING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Player exited, closes the screen and stops the game
                SECURE_SOCKET.send(pickle.dumps("exit"))
                pygame.quit()
                SECURE_SOCKET.close()
                return

        if WAITING:
            # If no one exited the waiting room
            WINDOW.fill(BACKGROUND_COLOR)
            font = pygame.font.SysFont(FONT_TYPE, 70)
            text = font.render("Waiting For Players...", True, TEXT_COLOR)
            # Displays the "waiting for players..." message
            WINDOW.blit(text, ((SCREEN_WIDTH - text.get_width()) / 2, (SCREEN_HEIGHT - text.get_height()) / 2 - 100))

            font2 = pygame.font.SysFont(FONT_TYPE, 50)
            if PLAYER.is_runner:
                text2 = font2.render("You Are The Runner", True, TEXT_COLOR)
            else:
                text2 = font2.render(f"You Are Catcher Number {PLAYER.catcher_number}", True, TEXT_COLOR)
            WINDOW.blit(text2, ((SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text2.get_height()) / 2 + 50))
            player_pic = pygame.image.load(PLAYER.img_address)
            player_pic = pygame.transform.scale(player_pic, (PLAYER_PIC_WIDTH_HEIGHT, PLAYER_PIC_WIDTH_HEIGHT))
            # Displays the player the client is going to play as
            WINDOW.blit(player_pic,
                        ((SCREEN_WIDTH - PLAYER_PIC_WIDTH_HEIGHT) / 2,
                         (SCREEN_HEIGHT - PLAYER_PIC_WIDTH_HEIGHT) / 2 + 200))

            pygame.display.update()

    if EXIT_CODE == PLAYER_EXITED_WAITING_CODE:
        # A player exited the game- a message is shown and the client is sent back to the home screen
        WINDOW.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(FONT_TYPE, 35)
        text1 = font.render("A Player Has Exited The Game!", True, TEXT_COLOR)
        text2 = font.render("You Are Being Sent Back To Home", True, TEXT_COLOR)
        # displays a message that a player has exited the game
        WINDOW.blit(text1, ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
        WINDOW.blit(text2, (
            (SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

        pygame.display.update()
        pygame.time.delay(2000)
        SECURE_SOCKET.send((pickle.dumps("clear")))
        EXIT_CODE = 0
        WAITING = True
        home_screen()
    elif EXIT_CODE == SERVER_TERMINATED_CODE:
        # The server Terminated- a message is shown and the client is sent back to the start screen
        WINDOW.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(FONT_TYPE, 35)
        text1 = font.render("The Server Terminated The Game", True, TEXT_COLOR)
        text2 = font.render("You Need To Login Again", True, TEXT_COLOR)
        # Displays a message that the server terminated
        WINDOW.blit(text1, ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
        WINDOW.blit(text2, (
            (SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

        pygame.display.update()
        pygame.time.delay(2000)
        SECURE_SOCKET.close()
        pygame.quit()
        EXIT_CODE = 0
        WAITING = True
        main()
    else:
        # All the players joined, starting the game
        play()


def create_map():
    """
    This function calls the Creator draw function then sends the server a map if the client saved it
    :return:
    """
    # calls the draw() function of Creator class that presents the window that the client can create a map with
    block_list = Creator().draw(WINDOW)
    if block_list is not None:
        # If the client saved the map
        try:
            # Sends the server the map for it to save in Maps.txt
            SECURE_SOCKET.send(pickle.dumps(block_list))
        except (socket.error, pickle.PickleError):
            # The server isn't active (it terminated)
            WINDOW.fill(BACKGROUND_COLOR)
            font = pygame.font.SysFont(FONT_TYPE, 35)
            text1 = font.render("The Server Terminated The Game", True, TEXT_COLOR)
            text2 = font.render("You Need To Login Again", True, TEXT_COLOR)
            WINDOW.blit(text1, ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
            WINDOW.blit(text2, (
                (SCREEN_WIDTH - text2.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))
            pygame.display.update()
            pygame.time.delay(2000)
            SECURE_SOCKET.close()
            pygame.quit()
            main()
    # Returns to the home screen
    home_screen()


def instructions():
    """
    This Function draws the instructions
    :return:
    """
    WINDOW.fill(BACKGROUND_COLOR)

    title_font = pygame.font.SysFont(FONT_TYPE, 110)
    title_text = title_font.render("Instructions", True, TEXT_COLOR)
    # Displays the title - "Instructions"
    WINDOW.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) / 2, 10))

    participants_font = pygame.font.SysFont(FONT_TYPE, 30)
    participants_text = participants_font.render("Participants:\n"
                                                 "1 Runner \n"
                                                 "1-6 Catchers", True, TEXT_COLOR)
    # Displays the participants
    WINDOW.blit(participants_text, (20, 180))

    # Displays the participant images
    WINDOW.blit(INSTRUCTIONS_CATCHERS_PICTURE, (200, 280))
    WINDOW.blit(INSTRUCTIONS_RUNNER_PICTURE, (150, 245))

    instructions_font = pygame.font.SysFont(FONT_TYPE, 30)
    instructions_text = instructions_font.render("The goal of the game is for the catchers to catch the \n"
                                                 " runner who is trying to run away from them.\n"
                                                 " The movement in the game is with the arrows on the \n keyboard.",
                                                 True,
                                                 TEXT_COLOR)
    # Displays the instructions
    WINDOW.blit(instructions_text, (20, 350))

    back_button = Button("Back to Home", (SCREEN_WIDTH - 400) / 2, SCREEN_HEIGHT * 0.8, TEXT_COLOR, BACKGROUND_COLOR,
                         400, 100, FONT_TYPE, 40)
    # displays the button
    back_button.draw(WINDOW)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Player exited, closes the screen and stops the game
                pygame.quit()
                SECURE_SOCKET.send(pickle.dumps("leave"))
                SECURE_SOCKET.close()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if back_button.click(pos):
                    # If the client pressed on the button to go back to the home screen
                    home_screen()
        pygame.display.update()


def home_screen():
    """
    This function draws the main home screen and starts the client process
    """
    global PLAYER

    pygame.display.set_caption("Maze Runner")

    WINDOW.fill(BACKGROUND_COLOR)
    WINDOW.blit(HOME_SCREEN_PLAYERS_PICTURE, ((SCREEN_WIDTH - HOME_SCREEN_PLAYERS_PICTURE.get_width()) / 2,
                                              (SCREEN_HEIGHT - HOME_SCREEN_PLAYERS_PICTURE.get_height()) / 2))

    font = pygame.font.SysFont(FONT_TYPE, 110)
    text = font.render("Maze Runner", True, TEXT_COLOR)
    # Displays the title - "Maze Runner"
    WINDOW.blit(text, ((SCREEN_WIDTH - text.get_width()) / 2, 10))

    # creates buttons
    buttons = [Button("Instructions", 15, 500, TEXT_COLOR, BACKGROUND_COLOR, 210, 100, FONT_TYPE, 37),
               Button("Start Game", 232, 500, TEXT_COLOR, BACKGROUND_COLOR, 210, 100, FONT_TYPE, 37),
               Button("Create Map", 450, 500, TEXT_COLOR, BACKGROUND_COLOR, 210, 100, FONT_TYPE, 37)]

    # displays the button
    for button in buttons:
        button.draw(WINDOW)

    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Player exited, closes the screen and stops the game
                pygame.quit()
                try:
                    SECURE_SOCKET.send(pickle.dumps("leave"))
                except (socket.error, pickle.PickleError):
                    # If the server is not active
                    SECURE_SOCKET.close()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                # player presses the mouse
                pos = pygame.mouse.get_pos()
                if buttons[0].click(pos):
                    # player pressed instructions
                    instructions()
                if buttons[2].click(pos):
                    # player pressed create map
                    create_map()
                if buttons[1].click(pos):
                    # player pressed start game
                    run = False
                    try:
                        # sends starting game
                        SECURE_SOCKET.send(pickle.dumps("start"))
                    except (pickle.PickleError, socket.error):
                        # Server terminated
                        WINDOW.fill(BACKGROUND_COLOR)
                        font = pygame.font.SysFont(FONT_TYPE, 35)
                        text1 = font.render("The Server Terminated The Game", True, TEXT_COLOR)
                        text2 = font.render("You Need To Login Again", True, TEXT_COLOR)
                        # Displays a message that the server terminated
                        WINDOW.blit(text1,
                                    ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
                        WINDOW.blit(text2, (
                            (SCREEN_WIDTH - text2.get_width()) / 2,
                            (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

                        pygame.display.update()
                        pygame.time.delay(2000)
                        SECURE_SOCKET.close()
                        pygame.quit()
                        main()
                    try:
                        # gets the player that the client plays as
                        PLAYER = pickle.loads(SECURE_SOCKET.recv(2048))
                    except (socket.error, pickle.PickleError):
                        # Server terminated
                        WINDOW.fill(BACKGROUND_COLOR)
                        font = pygame.font.SysFont(FONT_TYPE, 35)
                        text1 = font.render("The Server Terminated The Game", True, TEXT_COLOR)
                        text2 = font.render("You Need To Login Again", True, TEXT_COLOR)
                        # Displays a message that the server terminated
                        WINDOW.blit(text1,
                                    ((SCREEN_WIDTH - text1.get_width()) / 2, (SCREEN_HEIGHT - text1.get_height()) / 2))
                        WINDOW.blit(text2, (
                            (SCREEN_WIDTH - text2.get_width()) / 2,
                            (SCREEN_HEIGHT - text1.get_height()) / 2 + text1.get_height()))

                        pygame.display.update()
                        pygame.time.delay(2000)
                        SECURE_SOCKET.close()
                        pygame.quit()
                        main()
                    if PLAYER == TOO_MANY_PLAYERS_ERROR_CODE:
                        # There are too many players in the game, client can't join
                        WINDOW.fill(BACKGROUND_COLOR)
                        font = pygame.font.SysFont(FONT_TYPE, 40)
                        text = font.render("Can't Join Game, Too Much Players", True, TEXT_COLOR)
                        WINDOW.blit(text,
                                    ((SCREEN_WIDTH - text.get_width()) / 2, (SCREEN_HEIGHT - text.get_height()) / 2))
                        pygame.display.update()
                        pygame.time.delay(3000)
                        # goes back to home screen
                        home_screen()
                    else:
                        thread = threading.Thread(target=get_info_from_server)
                        thread.start()
                        waiting_screen()


def create_window():
    """
    This function creates the game window then calls the home_screen() function
    """
    global WINDOW
    WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.font.init()
    home_screen()


def login_screen(form, frame):
    """
    This function shows the login screen.
    :param form: The tkinter form that is shown
    :param frame: The designed screen
    """
    # destroys the earlier screen
    frame.destroy()
    form.title("Login form")
    # this is the size and the location of the small screen that opens up
    form.geometry(f'440x440+{MONITOR.width // 2 - 440 // 2}+{MONITOR.height // 2 - 440 // 2}')
    # This is the background color the will appear when making the screen bigger
    form.configure(bg='#808080')
    frame = tkinter.Frame(bg='#808080')

    # Creating labels, entries and buttons
    login_label = tkinter.Label(frame, text="Login", bg='#808080', fg="#282828", font=(FONT_TYPE, 30))
    username_label = tkinter.Label(frame, text="Username", bg='#808080', fg="#282828", font=(FONT_TYPE, 20))
    username_entry = tkinter.Entry(frame, font=(FONT_TYPE, 16))
    password_label = tkinter.Label(frame, text="Password", bg='#808080', fg="#282828", font=(FONT_TYPE, 20))
    password_entry = tkinter.Entry(frame, show="*", font=(FONT_TYPE, 16))
    login_button = tkinter.Button(frame, text="Login", bg="#282828", fg="#808080", font=(FONT_TYPE, 20),
                                  command=lambda: login(form, username_entry.get(), password_entry.get()))
    register_button = tkinter.Button(frame, text="Register", bg="#282828", fg="#808080", font=(FONT_TYPE, 10),
                                     command=lambda: register_screen(form, frame))

    # Places the buttons, labels and entries on the screen
    login_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=10)
    username_label.grid(row=1, column=0)
    username_entry.grid(row=1, column=1, pady=20)
    password_label.grid(row=2, column=0)
    password_entry.grid(row=2, column=1, pady=20)
    login_button.grid(row=3, column=0, columnspan=2, pady=20)
    register_button.grid(row=4, column=0, columnspan=2, pady=10)

    frame.pack()


def login(form, username, password):
    """
    This function handles the login and establishes connection with the server.
    If the login is complete the player is moved to the home screen
    :param form: The tkinter form that is shown
    :param username: The username the player chose
    :param password: The password the player chose
    """
    global SECURE_SOCKET

    # Creates a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Creates a SSL context
    context = ssl.create_default_context()
    # Establish a secure connection to the server
    context.load_verify_locations(cafile=CA_CERT)  # CA.pem is the certificate of the CA that I trust
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True  # Checks if the server's CA is one that I trust

    # wraps the socket to create a new secure socket
    SECURE_SOCKET = context.wrap_socket(client, server_hostname=SERVER_IP)
    try:
        # connects to the server
        SECURE_SOCKET.connect((SERVER_IP, SERVER_PORT))
        print("client connected")
    except socket.error as e:
        print(e)
        messagebox.showinfo(title="Connection to Server", message="Can't connect to server")
        return

    try:
        # Sends login info and receives if the login is successful
        SECURE_SOCKET.send(pickle.dumps(("login", username, password)))
        logged = pickle.loads((SECURE_SOCKET.recv(1024)))
    except (socket.error, pickle.PickleError):
        messagebox.showinfo(title="Connection to Server", message="Cant receive or send information to the server")
        return
    if logged:
        # Login successful
        form.destroy()
        create_window()
    else:
        messagebox.showerror(title="Error", message="Can't Login")
        SECURE_SOCKET.close()


def register_screen(form, frame):
    """
    This function shows the registration screen.
    :param form: The tkinter form that is shown
    :param frame: The designed screen
    """
    # destroys the earlier screen
    frame.destroy()
    form.title("Register form")
    # this is the size and the location of the small screen that opens up
    form.geometry(f'440x440+{MONITOR.width // 2 - 440 // 2}+{MONITOR.height // 2 - 440 // 2}')
    # This is the background color the will appear when making the screen bigger
    form.configure(bg='#808080')
    frame = tkinter.Frame(bg='#808080')

    # Creating labels, entries and buttons
    register_label = tkinter.Label(frame, text="Register", bg='#808080', fg="#282828", font=(FONT_TYPE, 30))
    username_label = tkinter.Label(frame, text="Username", bg='#808080', fg="#282828", font=(FONT_TYPE, 20))
    username_entry = tkinter.Entry(frame, font=(FONT_TYPE, 16))
    password_label = tkinter.Label(frame, text="Password", bg='#808080', fg="#282828", font=(FONT_TYPE, 20))
    password_entry = tkinter.Entry(frame, show="*", font=(FONT_TYPE, 16))
    password_validation_label = tkinter.Label(frame, text="Password\n Validation", bg='#808080', fg="#282828",
                                              font=(FONT_TYPE, 18))
    password_validation_entry = tkinter.Entry(frame, show="*", font=(FONT_TYPE, 16))
    login_button = tkinter.Button(frame, text="Login", bg="#282828", fg="#808080", font=(FONT_TYPE, 10),
                                  command=lambda: login_screen(form, frame))
    register_button = tkinter.Button(frame, text="Register", bg="#282828", fg="#808080", font=(FONT_TYPE, 15),
                                     command=lambda: register(form, username_entry.get(), password_entry.get(),
                                                              password_validation_entry.get()))

    # Places the buttons, labels and entries on the screen
    register_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=10)
    username_label.grid(row=1, column=0)
    username_entry.grid(row=1, column=1, pady=15)
    password_label.grid(row=2, column=0)
    password_entry.grid(row=2, column=1, pady=15)
    password_validation_label.grid(row=3, column=0)
    password_validation_entry.grid(row=3, column=1, pady=15)
    register_button.grid(row=4, column=0, columnspan=2, pady=10)
    login_button.grid(row=5, column=0, columnspan=2, pady=15)

    frame.pack()


def register(form, username, password, password_validation):
    """
    This function handles the registration and establishes connection with the server.
    If the registration is complete the player is moved to the home screen
    :param form: The tkinter form that is shown
    :param username: The username the player chose
    :param password: The password the player chose
    :param password_validation: The password again for validation
    """
    global SECURE_SOCKET

    if password.strip() == "" or username.strip() == "":
        messagebox.showinfo(title="Can't Register", message="Both the username or password cannot be empty")

    if password != password_validation:
        messagebox.showinfo(title="Can't Register", message="The passwords are not the same")
        return

    # Creates a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Creates a SSL context
    context = ssl.create_default_context()
    # Establish a secure connection to the server
    context.load_verify_locations(cafile=CA_CERT)  # CA.pem is the certificate of the CA that I trust
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True  # Checks if the server's CA is one that I trust

    # wraps the socket to create a new secure socket
    SECURE_SOCKET = context.wrap_socket(client, server_hostname=SERVER_IP)
    try:
        # connects to the server
        SECURE_SOCKET.connect((SERVER_IP, SERVER_PORT))
        print("client connected")
    except socket.error:
        messagebox.showinfo(title="Connection to Server", message="Can't connect to server")
        return
    try:
        # Sends registration info and receives if the registration is successful
        SECURE_SOCKET.send(pickle.dumps(("register", username, password)))
        registered = pickle.loads((SECURE_SOCKET.recv(1024)))
    except (socket.error, pickle.PickleError):
        messagebox.showinfo(title="Connection to Server", message="Cant receive or send information to the server")
        return
    if registered:
        # Registration successful
        form.destroy()
        create_window()
    else:
        messagebox.showerror(title="Can't Register", message="Can't Register. Username is already used")
        SECURE_SOCKET.close()


def main():
    """
    This function creates the home tkinter form-
    User can choose to register or login
    """
    form = tkinter.Tk()
    form.title("Home Screen")
    # this is the size and the location of the small screen that opens up
    form.geometry(f'440x440+{MONITOR.width // 2 - 440 // 2}+{MONITOR.height // 2 - 440 // 2}')
    # This is the background color the will appear when making the screen bigger
    form.configure(bg='#808080')
    # this is the screen
    frame = tkinter.Frame(bg='#808080')

    # creates the title label
    welcome_label = tkinter.Label(frame, text="Welcome", bg='#808080', fg="#282828", font=(FONT_TYPE, 50))

    # Creates buttons
    login_button = tkinter.Button(frame, text=" Login ", bg="#282828", fg="#808080", font=(FONT_TYPE, 20),
                                  command=lambda: login_screen(form, frame))
    register_button = tkinter.Button(frame, text="Register", bg="#282828", fg="#808080", font=(FONT_TYPE, 20),
                                     command=lambda: register_screen(form, frame))

    # Places the buttons and labels on the screen
    login_button.grid(row=1, column=0, columnspan=2, pady=20)
    register_button.grid(row=2, column=0, columnspan=2, pady=30)
    welcome_label.grid(row=0, column=0, columnspan=2, sticky="news", pady=30)
    frame.pack()
    form.mainloop()


if __name__ == '__main__':
    main()
