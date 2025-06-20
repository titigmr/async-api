
# import asyncio
# from time import sleep
# from typing import Annotated

# from fastapi import Depends
# from fastapi_injectable import injectable

# from api.core.brokers.rabbitmq import RabbitMQBroker
import asyncio
from time import sleep
from listener.core.di_container import DIContainer

async def main():
    container = DIContainer()
    print("started.")
    await container.app().start()
    print("started.")


if __name__ == "__main__":
    asyncio.run(main()) 
    while True:
        sleep(10)

# import signal
# import sys

# def sigint_handler(signal, frame):
#     print('Interrupted')
#     sys.exit(0)
# signal.signal(signal.SIGINT, sigint_handler)
# signal.signal(signal.SIGTERM, sigint_handler)




# import asyncio
# import aio_pika

# RABBITMQ_URL = "amqp://kalo:kalo@127.0.0.1:5672/"

# async def process_message(message: aio_pika.IncomingMessage):
#     async with message.process():  # auto-ack à la fin du bloc
#         print(f"[x] Traitement de {message.body.decode()}")
#         await asyncio.sleep(2)
#         print(f"[✓] Fini {message.body.decode()}")

# async def message_handler(message: aio_pika.IncomingMessage):
#     # Lance le traitement sans attendre (non bloquant)
#     asyncio.create_task(process_message(message))

# async def main():
#     connection = await aio_pika.connect_robust(RABBITMQ_URL)
#     channel = await connection.channel()
#     await channel.set_qos(prefetch_count=5)  # autorise jusqu’à 10 messages non ack

#     queue = await channel.declare_queue("ma_queue", durable=True)
#     await queue.consume(message_handler)

#     print("[*] En attente des messages (Ctrl+C pour quitter)...")
#     await asyncio.Event().wait()  # attend indéfiniment

# if __name__ == "__main__":
#     asyncio.run(main())
