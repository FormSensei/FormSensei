import pika
from PIL import Image
import os

QUEUE_NAME = "image_resize"

def resize_image(input_path, output_path, size=(128, 128)):
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size)
            img.save(output_path)
            print(f"Resized image saved to: {output_path}")
    except Exception as e:
        print(f"Error resizing image: {e}")

def callback(ch, method, properties, body):
    file_path = body.decode("utf-8")
    output_path = file_path.replace("uploads", "uploads/reduced")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    resize_image(file_path, output_path)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    print("Waiting for messages...")
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
