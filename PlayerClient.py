import os
import json
from dotenv import load_dotenv

import threading
import paho.mqtt.client as paho
from paho import mqtt
import time

player_1 = ""
team_name = ""

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
    if(player_1 not in msg.topic and "scores" not in msg.topic):  #Prevents other player's info from showing.
        return
    print("message: " + msg.topic + " " + str(msg.qos))
    try:
        fullPlayDetails = json.loads((msg.payload).decode('utf-8'))
        for key, value in fullPlayDetails.items():
            print(f"{key}: {value}")
    except:
        print(msg.payload)
    
    # move2 = input('\nEnter your move: \n')
    # if move2 == "STOP":
    #     time.sleep(1)
    #     client.publish(f"games/{lobby_name}/start", "STOP")
    #     time.sleep(1)
    # else:
    #     time.sleep(1)
    #     client.publish(f"games/{lobby_name}/{player_1}/move", move2)
    #     time.sleep(1)


if __name__ == '__main__':
    print("ONLY SHOWING YOUR OWN INFORMATION.")
    load_dotenv(dotenv_path='./credentials.env')

    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    
    player_1 = input("Please input the Player Name: ")

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id=f"{player_1}",
                         userdata=None, protocol=paho.MQTTv5)

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe  # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish  # Can comment out to not print when publishing to topics

    lobby_name = input("Please input the Lobby Name: ")
    team_name = input("Please input the team name: ")

    client.loop_start()

    client.subscribe(f"games/+/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/+/scores')

    # player_2 = "Player2"
    # player_3 = "Player3"


    client.publish("new_game", json.dumps({'lobby_name': lobby_name,
                                           'team_name': team_name,
                                           'player_name': player_1}))
    client.publish(f"games/{lobby_name}/start", "START")


    # First implement player 1 for one user_controllable agent

    # client.publish("new_game", json.dumps({'lobby_name': lobby_name,
    #                                        'team_name': 'BTeam',
    #                                        'player_name': player_2}))
    #
    # client.publish("new_game", json.dumps({'lobby_name': lobby_name,
    #                                        'team_name': 'BTeam',
    #                                        'player_name': player_3}))

 



    while True:        
        wordInput = input('Enter your move: \n')
        if(wordInput in ["UP", "DOWN", "RIGHT", "LEFT"]):
            client.publish(f"games/{lobby_name}/{player_1}/move", wordInput)
