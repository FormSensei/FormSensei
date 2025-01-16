import pika
from PIL import Image
import os
import logging
import time

logging.basicConfig(
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler(),        # Log to console
    ]
)
logger = logging.getLogger(__name__)

QUEUE_NAME = "image_resize"

def resize_image(input_path, output_path, size=(128, 128)):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size)
            img.save(output_path)
            logger.info(f"Resized image saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error resizing image: {e}")

def callback(ch, method, properties, body):
    file_path = body.decode("utf-8")
    input_path = os.path.join("uploads/full", file_path)
    output_path = os.path.join("uploads/reduced", file_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    resize_image(input_path, output_path)

def main():
    check = True
    while (check):
        try:
            time.sleep(1)
            logger.info("Trying to connect!")
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            check = False
        except Exception as e:
            logger.error("Error while trying to connect: {e}")
    
    logger.info("Connection sucsessful!")
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    logger.info("Waiting for messages...")
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
