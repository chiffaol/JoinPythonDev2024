import asyncio
import cowsay

# Словарь для хранения зарегистрированных пользователей
registered_users = {}

async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    cow_name = None

    while True:
        data = await reader.readline()
        message = data.decode().strip()

        if not message:
            break

        parts = message.split(maxsplit=1)
        command = parts[0].lower()

        if command == 'login':
            if len(parts) == 2:
                cow_name = parts[1]
                if cow_name in registered_users.values():
                    await writer.write('This cow name is already taken. Choose another one.\n'.encode())
                else:
                    registered_users[peername] = cow_name
                    await writer.write(f'Logged in as {cow_name}\n'.encode())
            else:
                await writer.write('Usage: login <cow_name>\n'.encode())

        elif command == 'say':
            if len(parts) == 2 and cow_name:
                recipient_cow = parts[1]
                for peer, name in registered_users.items():
                    if name == recipient_cow:
                        recipient_writer = asyncio.StreamWriter(peer, None, None, reader, writer, loop)
                        message_to_send = f'{cow_name} says: {parts[1]}'
                        await recipient_writer.write(message_to_send.encode() + b'\n')
                        await recipient_writer.drain()
                        break
            else:
                await writer.write('Usage: say <recipient_cow> <message>\n'.encode())

        elif command == 'yield':
            if len(parts) == 2 and cow_name:
                message_to_send = f'{cow_name} says: {parts[1]}'
                for peer, name in registered_users.items():
                    if peer != peername:
                        recipient_writer = asyncio.StreamWriter(peer, None, None, reader, writer, loop)
                        await recipient_writer.write(message_to_send.encode() + b'\n')
                        await recipient_writer.drain()
            else:
                await writer.write('Usage: yield <message>\n'.encode())

        elif command == 'who':
            await writer.write('Registered cows:\n'.encode())
            for name in registered_users.values():
                await writer.write(f'- {name}\n'.encode())

        elif command == 'cows':
            all_cows = cowsay.get_cow_list()
            taken_cows = set(registered_users.values())
            available_cows = [cow for cow in all_cows if cow not in taken_cows]
            await writer.write('Available cows:\n'.encode())
            for cow in available_cows:
                await writer.write(f'- {cow}\n'.encode())

        elif command == 'quit':
            break

        else:
            await writer.write('Unknown command\n'.encode())

    del registered_users[peername]
    writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
