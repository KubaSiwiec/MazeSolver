# import required libraries
import struct
import zmq
import operator

# import time


# establish the connection
ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:6574")
req.send(b"reset")
req.recv()


"""
Functions for changing the data representation
"""


def cell_position_to_number(pos_x, pos_y):
    return pos_y + 16 * pos_x


def orientation_to_direction(orientation, left, front, right):
    north, west, south, east = 0, 0, 0, 0
    if orientation == 1:
        west = left
        north = front
        east = right
    elif orientation == 4:
        west = front
        north = right
        south = left
    elif orientation == 3:
        west = right
        south = front
        east = left
    elif orientation == 2:
        north = left
        east = front
        south = right

    return north, west, south, east


def orientation_to_byte(orientation):
    # 1N, 2W, 3S, 4E
    if orientation == 1:
        return b"N"
    if orientation == 2:
        return b"E"
    if orientation == 3:
        return b"S"
    if orientation == 4:
        return b"W"


"""
Read walls of the maze, writing map to the robot's memory, update state of it on the server
"""


def read_walls(pos_x, pos_y, orientation):
    req.send(b"W" + struct.pack("2B", pos_x, pos_y) + orientation_to_byte(orientation))

    # read walls as unpacking the server response
    left, front, right = struct.unpack("3B", req.recv())
    return {"left": left, "front": front, "right": right}


def write_cell_walls(pos_x, pos_y, orientation):
    numbers[cell_position_to_number(pos_x, pos_y)] += 1
    if was_visited(pos_x, pos_y):
        pass
    else:
        cell_byte = 0x01  # starting from 1, because cell is being visited now
        are_there_walls = read_walls(pos_x, pos_y, orientation)
        left, front, right = are_there_walls.values()
        north, west, south, east = orientation_to_direction(
            orientation, left, front, right
        )
        # print("Position: {}, {}, or {};".format(pos_x, pos_y, orientation), end="    ")
        # print("Left {}, front {}, right {};".format(left, front, right), end="    ")
        # print("north {}, west {}, south {}, east {}".format(north, west, south, east))
        if east:
            cell_byte = cell_byte + 2
        if south:
            cell_byte = cell_byte + 4
        if west:
            cell_byte = cell_byte + 8
        if north:
            cell_byte = cell_byte + 16

        walls[cell_position_to_number(pos_x, pos_y)] = cell_byte
    # in brute force search numbers list should be used as mark how many times the cell was visited
    # then after mapping numbers list should be cleared and used as indicator how far from the center of the labirynth is the cell


def update_state(pos_x, pos_y, orientation):
    state = b"S" + struct.pack("2B", pos_x, pos_y) + orientation_to_byte(orientation)
    state += b"F"
    state += struct.pack("256B", *numbers)
    state += b"F"
    state += struct.pack("256B", *walls)
    req.send(state)
    req.recv()


"""
Checking functions
"""


def was_visited(pos_x, pos_y):
    cell_nb = cell_position_to_number(pos_x, pos_y)
    if walls[cell_nb] % 2 == 0:
        return False
    else:
        return True


def are_all_cells_visited():
    for i in range(16):
        for j in range(16):
            if was_visited(i, j):
                continue
            else:
                return False
    return True


"""
Decision functions
They are responsible for checking weights of the surrounding cells and taking the one with the
lowest weight as the direction to turn, if it is not beyond the wall
"""


def get_cell_weight(pos_x, pos_y, orientation):

    # check if the robot is not on the border of the labirynth, and assign weights

    # if north
    if orientation == 1:
        weight_on_left = (
            numbers[cell_position_to_number(pos_x - 1, pos_y)] if pos_x != 0 else 100000
        )
        weight_on_front = (
            numbers[cell_position_to_number(pos_x, pos_y + 1)]
            if pos_y != 15
            else 100000
        )
        weight_on_right = (
            numbers[cell_position_to_number(pos_x + 1, pos_y)]
            if pos_x != 15
            else 100000
        )

    # if east
    if orientation == 2:
        weight_on_left = (
            numbers[cell_position_to_number(pos_x, pos_y + 1)]
            if pos_y != 15
            else 100000
        )
        weight_on_front = (
            numbers[cell_position_to_number(pos_x + 1, pos_y)]
            if pos_x != 15
            else 100000
        )
        weight_on_right = (
            numbers[cell_position_to_number(pos_x, pos_y - 1)] if pos_y != 0 else 100000
        )

    # if south
    if orientation == 3:
        weight_on_left = (
            numbers[cell_position_to_number(pos_x + 1, pos_y)]
            if pos_x != 15
            else 100000
        )
        weight_on_front = (
            numbers[cell_position_to_number(pos_x, pos_y - 1)] if pos_y != 0 else 100000
        )
        weight_on_right = (
            numbers[cell_position_to_number(pos_x - 1, pos_y)] if pos_x != 0 else 100000
        )

    # if west
    if orientation == 4:
        weight_on_left = (
            numbers[cell_position_to_number(pos_x, pos_y - 1)]
            if pos_y != 15
            else 100000
        )
        weight_on_front = (
            numbers[cell_position_to_number(pos_x - 1, pos_y)] if pos_x != 0 else 100000
        )
        weight_on_right = (
            numbers[cell_position_to_number(pos_x, pos_y + 1)]
            if pos_x != 15
            else 100000
        )

    return {"left": weight_on_left, "front": weight_on_front, "right": weight_on_right}


def choose_where_to_turn(orientation, weights, are_there_walls):
    sorted_weights = sorted(weights.items(), key=operator.itemgetter(1))
    for key, value in sorted_weights:
        if are_there_walls[key] == 0:
            orient = turn(orientation, key)
            break
        else:
            # go backwards
            orient = turn(orientation, "left")
            orient = turn(orient, "left")
    return orient


"""
Action functions
Functions to change robots orientation and position 

"""


def turn(orientation, turn_dir):
    if turn_dir == "right":
        # print("is turning right")
        if orientation != 4:
            return orientation + 1
        else:
            return 1
    elif turn_dir == "left":
        # print("is turning left")
        if orientation != 1:
            return orientation - 1
        else:
            return 4
    else:
        return orientation


def move(pos_x, pos_y, orientation):
    if orientation == 1:
        pos_y = pos_y + 1
    elif orientation == 2:
        pos_x = pos_x + 1
    elif orientation == 3:
        pos_y = pos_y - 1
    elif orientation == 4:
        pos_x = pos_x - 1

    return pos_x, pos_y


# number informs about how many times was the cell visited - in brute force
# number informs about the distance of specific cell to the center in flood fill
# numbers[0] - SW, numbers[15] - NW, numbers[240] - SE, numbers[255] - NE
numbers = [0] * 256

# walls
# 000NWSEP - byte structure
# P - 1, E - 2, S - 4, W - 8, N - 16
# p tells if the cell was visited, N if there is wall in the north, W west, E east, and S - south
walls = [0] * 256
