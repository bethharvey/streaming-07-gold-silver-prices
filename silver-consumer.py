"""
    This program listens for work messages contiously. 
    If the price of silver is above $27 or below $15, a silver alert is sent.

    Author: Beth Harvey
    Date: October 2, 2023

"""

import pika
import sys
from collections import deque

# Import function to send email alerts
from email_alerts import createAndSendEmailAlert

# Configure logging
from util_logger import setup_logger

logger, logname = setup_logger(__file__)

# declare deque length
SILVER_DEQUE = deque(maxlen=7)


# define a callback function to be called when a message is received
def silver_callback(ch, method, properties, body):
    """
    Define behavior on getting a message.
    Receives a message from the queue,
    extracts silver price from the message,
    calculates price difference over a given time period,
    and sends an alert if the price is above or below a certain value.
    """

    # decode the binary message body to a string
    logger.info(f" [x] Received {body.decode()}")

    try:
        # process silver queue message
        silver_mess = body.decode().split(",")
        # add price to deque
        silver_price = float(silver_mess[1])
        silver_date = silver_mess[0]
        SILVER_DEQUE.append(silver_price)

        # calculate change in price over past week and since previous day
        if len(SILVER_DEQUE) > 1:
            week_change = round(SILVER_DEQUE[0] - SILVER_DEQUE[-1],2)
            day_change = round(SILVER_DEQUE[-2] - SILVER_DEQUE[-1],2)

            # check for price over $27 and send alert
            if silver_price > 27:
                    logger.info(
                        f"""Silver price alert on {silver_date}! The price of silver is ${silver_price}, so now might be a good time to sell!
                        That's a ${week_change} change since last week and a ${day_change} change since yesterday."""
                    )
                    email_subject = "Silver High Price Alert"
                    email_body = f"""Silver price alert on {silver_date}! The price of silver is ${silver_price}, so now might be a good time to sell!
                        That's a ${week_change} change since last week and a ${day_change} change since yesterday."""
                    createAndSendEmailAlert(email_subject, email_body)

            # check for price under $15 and send alert
            if silver_price < 15:
                    logger.info(
                        f"""Silver price alert on {silver_date}! The price of silver is ${silver_price}, so now might be a good time to buy!
                        That's a ${week_change} change since last week and a ${day_change} change since yesterday."""
                    )
                    email_subject = "Silver Low Price Alert"
                    email_body = f"""Silver price alert on {silver_date}! The price of silver is ${silver_price}, so now might be a good time to buy!
                    That's a ${week_change} change since last week and a ${day_change} change since yesterday."""
                    createAndSendEmailAlert(email_subject, email_body)        
        # when done with task, tell the user
        logger.info(" [x] Processed silver price.")
        # acknowledge the message was received and processed
        # (now it can be deleted from the queue)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error("An error has occurred with the silver message.")
        logger.error(f"The error says: {e}.")


# define a main function to run the program
def main(hn: str = "localhost", qn: str = "task_queue"):
    """Continuously listen for task messages on a named queue."""

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        logger.error("ERROR: connection to RabbitMQ server failed.")
        logger.error(f"Verify the server is running on host={hn}.")
        logger.error(f"The error says: {e}")
        sys.exit(1)

    try:
        # use the connection to create a communication channel
        channel = connection.channel()

        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        channel.queue_declare(queue=qn, durable=True)

        # The QoS level controls the # of messages
        # that can be in-flight (unacknowledged by the consumer)
        # at any given time.
        # Set the prefetch count to one to limit the number of messages
        # being consumed and processed concurrently.
        # This helps prevent a worker from becoming overwhelmed
        # and improve the overall system performance.
        # prefetch_count = Per consumer limit of unaknowledged messages
        channel.basic_qos(prefetch_count=1)

        # configure the channel to listen on a specific queue,
        # use the callback function named callback,
        # and do not auto-acknowledge the message (let the callback handle it)
        channel.basic_consume(
            queue=qn, on_message_callback=silver_callback, auto_ack=False
        )

        # print a message to the console for the user
        logger.info(" [*] Ready for work. To exit press CTRL+C")

        # start consuming messages via the communication channel
        channel.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        logger.error("ERROR: something went wrong.")
        logger.error(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()


# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    # call the main function with the information needed
    main("localhost", "02-silver")
