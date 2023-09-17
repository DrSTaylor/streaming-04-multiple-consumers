"""
    This program sends a message to a queue on the RabbitMQ server.
    Make tasks harder/longer-running by adding dots at the end of the message.
    Modify your producer to slowly read tasks from tasks.csv instead of the console

    Author: Sara Taylor
    Date: September 17, 2023

"""


import pika
import sys
import webbrowser
import logging
import time
import csv

from util_logger import setup_logger
logger, logname = setup_logger(__file__)



INPUT_FILE_NAME = ("\tasks.csv")

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent {message}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()
    
def send_csv_messages (host: str, queue_name: str, input_file_name: csv):
    """
    Read input CSV file and send each row as a message to the listening_workers.
    
    Parameters:
        input_file_name (str): The name of the CSV file
        host (str): host name or IP address of the rabbitmq server
        queue_name (str): the name of the queue
    """
    try:

        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        ch.queue_declare(queue=queue_name, durable=True)

        logger.info(f"Reading messages from {input_file_name}...")
        with open(input_file_name, 'r') as input_file:
            reader = csv.reader(input_file)
            for row in reader:
                # join the elements in a row into a single message
                message = " ".join(row)
                # send the message to the queue
                send_message("localhost", "CSV_task", "tasks.csv")


    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # Close the connection to the server
        conn.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # ask the user if they'd like to open the RabbitMQ Admin site
    # true shows the offer/false turns off the offer for the user
    offer_rabbitmq_admin_site()

    # Send messages from the CSV file and send them to RabbitMQ
    send_csv_messages("localhost", "CSV_task", "tasks.csv")
