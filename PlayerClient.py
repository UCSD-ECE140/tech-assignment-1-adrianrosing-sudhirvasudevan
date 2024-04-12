import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random
import counter

player_1 = ""
team_name = ""
endGame = False

start_game = False

currentPos = []
currentWalls = []
currentCoins = []
currentMovement = 2

continueWithNextMoveFlag = False

graph = [[0 for _ in range(10)] for _ in range(10)]


# Builds a small graph of what the player is currently seeing.
def build_graph():
    # print("Building Graph: ")

    global graph
    global currentPos
    global currentWalls
    global currentCoins

    global currentMovement

    for wall in currentWalls:
        x, y = wall
        graph[x][y] = -1  # wall cells are -1
    for coin in currentCoins:
        x, y = coin
        graph[x][y] = 1  # coin cells as 1
    x, y = currentPos
    graph[x][y] = currentMovement  # set current position to 2.
    currentMovement += 1

    currentCoins = []
    currentWalls = []

    # Debugging.
    # for i in graph:
    #     print(i)

    global continueWithNextMoveFlag
    continueWithNextMoveFlag = True


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    try:
        global start_game
        global endGame
        if "START" in msg.payload.decode('utf-8'):
            start_game = True
            return
        if "stop" in msg.payload.decode('utf-8'):
            print(msg.payload.decode('utf-8'))
            endGame = True
        # if team_name in msg.payload.decode('utf-8'):
        #     # do nothing
    except:
        print(msg.payload)
        print("Line 69 Running.")

    if (
            player_1 not in msg.topic and "scores" not in msg.topic and "stop" not in msg.topic):  # Prevents other player's info from showing.
        return
    print("message: " + msg.topic + " " + str(msg.qos))
    try:
        fullPlayDetails = json.loads(msg.payload.decode('utf-8'))

        for key, value in fullPlayDetails.items():

            if ("game_state" in msg.topic):
                if ("coin" in key):
                    global currentCoins
                    for i in value:
                        currentCoins.append(i)
                if ("walls" in key):
                    global currentWalls
                    currentWalls = value
                if ("currentPosition" in key):
                    global currentPos
                    currentPos = value

            print(f"{key}: {value}")
        if ("game_state" in msg.topic):
            build_graph()
    except:
        print(msg.payload)


def create_next_move():
    if (endGame == True):
        return "STOP"
    possibleMoves = ["UP", "DOWN", "RIGHT", "LEFT"]

    global currentCoins
    global currentPos
    global graph

    if not currentPos:
        print("No Current Position Given.")
        return random.choice(possibleMoves)

    valid_moves = []
    print("Current Pos: ", currentPos)

    # Check if moving UP is valid
    if currentPos[0] > 0 and graph[currentPos[0] - 1][currentPos[1]] != -1:
        valid_moves.append("UP")

        if graph[currentPos[0] - 1][
            currentPos[1]] < 2:  # If player has not already been there, adds additional weighting.
            for i in range(5):
                valid_moves.append("UP")

        if graph[currentPos[0] - 1][currentPos[1]] == 1:  # If coin is nearby:
            for i in range(40):
                valid_moves.append("UP")

    # Check if moving DOWN is valid
    if currentPos[0] < len(graph) - 1 and graph[currentPos[0] + 1][currentPos[1]] != -1:
        valid_moves.append("DOWN")

        if graph[currentPos[0] + 1][currentPos[1]] < 2:
            for i in range(5):
                valid_moves.append("DOWN")

        if graph[currentPos[0] + 1][currentPos[1]] == 1:  # If coin is nearby:
            for i in range(40):
                valid_moves.append("DOWN")

    # Check if moving LEFT is valid
    if currentPos[1] > 0 and graph[currentPos[0]][currentPos[1] - 1] != -1:
        valid_moves.append("LEFT")

        if graph[currentPos[0]][currentPos[1] - 1] < 2:
            for i in range(5):
                valid_moves.append("LEFT")

        if graph[currentPos[0]][currentPos[1] - 1] == 1:  # If coin is nearby:
            for i in range(40):
                valid_moves.append("LEFT")

    # Check if moving RIGHT is valid
    if currentPos[1] < len(graph[0]) - 1 and graph[currentPos[0]][currentPos[1] + 1] != -1:
        valid_moves.append("RIGHT")

        if graph[currentPos[0]][currentPos[1] + 1] < 2:
            for i in range(5):
                valid_moves.append("RIGHT")

        if graph[currentPos[0]][currentPos[1] + 1] == 1:  # If coin is nearby:
            for i in range(40):
                valid_moves.append("RIGHT")

    # print(valid_moves)

    ## A FEW THINGS WE COULD ADD TO MAKE THIS RUN BETTER:
    # 1) Tend to walk down paths that are older (i.e. smaller numbers) - (this might make it worse)
    # 2) Drastically decrease the probability of going left then right. 
    # 3) Clear coins which have been consumed by other players. This would be done by removing the 1s in the other function.

    return random.choice(valid_moves)


if __name__ == '__main__':
    print("ONLY SHOWING YOUR OWN INFORMATION.")
    load_dotenv(dotenv_path='./credentials.env')

    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    player_1 = input("Please input the Player Name: ")
    print(f"{player_1}")
    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1,
                         client_id=f"{player_1}",
                         userdata=None, protocol=paho.MQTTv5)
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)
    # setting callbacks, use separate functions like above for better visibility
    # client.on_subscribe = on_subscribe  # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    # client.on_publish = on_publish  # Can comment out to not print when publishing to topics

    lobby_name = input("Please input the Lobby Name: ")
    team_name = input("Please input the Team Name: ")

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/+/scores')

    client.publish("new_game", json.dumps({'lobby_name': lobby_name,
                                           'team_name': team_name,
                                           'player_name': player_1}))
    counter.add()

    # should we start game
    start_game = input("Type START in order to access the game.\n")

    while start_game != "START":
        client.subscribe(f'games/{lobby_name}/+/game_state')
        time.sleep(2)

    counter.subtract()

    while counter.get() != 0:
        time.sleep(1)

    client.publish(f"games/{lobby_name}/start", "START")

    client.loop_start()

    # First implement player 1 for one user_controllable agent
    # client.publish("new_game", json.dumps({'lobby_name': lobby_name,
    #                                        'team_name': 'BTeam',
    #                                        'player_name': player_2}))
    #
    # client.publish("new_game", json.dumps({'lobby_name': lobby_name,
    #                                        'team_name': 'BTeam',
    #                                        'player_name': player_3}))

    while True:
        # wordInput = input('Enter your move: \n')
        while not continueWithNextMoveFlag:
            time.sleep(.5)

        continueWithNextMoveFlag = False

        wordInput = create_next_move()
        # print("Next Move: ", wordInput)
        time.sleep(.5)
        if (wordInput in ["UP", "DOWN", "RIGHT", "LEFT"]):
            client.publish(f"games/{lobby_name}/{player_1}/move", wordInput)
            time.sleep(1)
        elif wordInput == "STOP":
            client.publish(f"games/{lobby_name}/start", "STOP")
            break
        else:
            print("ERROR", wordInput)
