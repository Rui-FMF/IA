import asyncio
import getpass
import json
import os
import time

import websockets
from mapa import Map
from consts import Tiles
from tree_search import *
import math


async def solver(puzzle, solution):
    while True:
        game_properties = await puzzle.get()
        mapa = Map(game_properties["map"])
        inittime = time.time()
        print('Level ', mapa._level)
        print("Solving Map:")
        print(mapa)

        max_x, max_y = mapa.size
        initial = (set(mapa.boxes), mapa.keeper)
        goals = mapa.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
        p = SearchProblem(Sokoban(max_y,max_x,mapa._map),initial,goals)
        if len(mapa.boxes) > 4:
            t = SearchTree(p, 'greedy')
        else:
            t = SearchTree(p, 'a*')
        path = await t.async_search()

        plan = t.plan
        print('time=',time.time()-inittime)
        print(t.open_nodes.qsize(),' nodes')

        keys = ""
        counter = 0
        for action in plan:
            move,box_pos,nbox_pos = action
            box_x,box_y = box_pos

            if move == "pu":
                goal_pos = (box_x,box_y+1)  #Position man need to be in to push
                last_key = "w"
            elif move == "pl":
                goal_pos = (box_x+1,box_y)
                last_key = "a"
            elif move == "pd":
                goal_pos = (box_x,box_y-1)
                last_key = "s"
            elif move == "pr":
                goal_pos = (box_x-1,box_y)
                last_key = "d"

            state = path[counter]
            mp = SearchProblem(Man(max_y,max_x,mapa._map),state,goal_pos)
            mt = SearchTreeMan(mp, 'a*')
            mt.search()
            for a in mt.plan:
                keys+=a[0]
            keys+=last_key
            counter+=1
            
        print("keys:")
        print(keys)
        await solution.put(keys)

async def agent_loop(puzzle, solution, server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    game_properties = update
                    keys = ""
                    await puzzle.put(game_properties)

                if not solution.empty():
                    keys = await solution.get()


                key = ""
                if len(keys):  # we got a solution!
                    key = keys[0]
                    keys = keys[1:]

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return



# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())

puzzle = asyncio.Queue(loop=loop)
solution = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle, solution, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle, solution))

loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()
