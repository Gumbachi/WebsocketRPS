import asyncio
import os
import uuid

import websockets
from websockets.exceptions import ConnectionClosedOK

moves = ["rock", "paper", "scissors"]

def check_win(p1move: str, p2move: str) -> str:
    match (p1move, p2move):
        case ("rock", "scissors") | ("paper", "rock") | ("scissors", "paper"):
            return "Player One Wins!!!"
        case ("scissors", "rock") | ("rock", "paper") | ("paper", "scissors"):
            return "Player Two Wins!!!"
        case _:
            return "Its a Tie. How Disappointing :("

async def patch_me_in():
    """Init connection to websocket or fail if the server is kil."""
    print("Connecting...")

    id = str(uuid.uuid1())
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/{id}") as websocket:
        print("Connected.")

        resp = await websocket.recv()
        print(resp)

        print("Waiting for other player to connect...")

        # wait for the go ahead so both players are connected
        while True:
            resp = await websocket.recv()
            if resp == "GO":
                break
        
        try:
            while move := input("Type out your move ('rock', 'paper', 'scissors') >> "):
                if move in moves:
                    break

            await websocket.send(move)

            print("Awaiting The Other Player's Move...")

            while True:
                resp: str = await websocket.recv()

                if resp == "GO":
                    continue

                if resp.startswith("GAME"):
                    movestrings = resp.split("\n")[1:]
                    p1move = movestrings[0][4:]
                    p2move = movestrings[1][4:]

                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Player One played {p1move.capitalize()}")
                    print(f"Player Two played {p2move.capitalize()}")
                    print(check_win(p1move, p2move))
                    break

                print(resp)
        except ConnectionClosedOK:
            pass


async def main():
    await patch_me_in()


if __name__ == "__main__":
     asyncio.get_event_loop().run_until_complete(main())