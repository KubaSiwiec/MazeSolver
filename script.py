# import zmq
# import struct

# ctx = zmq.Context()
# req = ctx.socket(zmq.REQ)
# req.connect('tcp://127.0.0.1:6574')

# #send information about position and orientation, send structure (2 position bytes, x=0, y=1), orientation to north
# req.send(b'W' + struct.pack('2B', 1, 1) + b'N')

# #read walls as unpacking the server response
# left, front, right = struct.unpack('3B', req.recv())
# print(left, front, right)


# import required libraries
import struct
import zmq


# establish the connection
ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:6574")
req.send(b"reset")
req.recv()


def set_bit(value, bit):
    return value | (1 << bit)


def clear_bit(value, bit):
    return value & ~(1 << bit)


def read_walls(pos_x, pos_y, orientation):
    req.send(b"W" + struct.pack("2B", pos_x, pos_y) + orientation_to_byte(orientation))

    # read walls as unpacking the server response
    left, front, right = struct.unpack("3B", req.recv())
    return left, front, right


def cell_position_to_number(pos_x, pos_y):
    return pos_y + 16 * pos_x


def was_visited(pos_x, pos_y):
    cell_nb = cell_position_to_number(pos_x, pos_y)
    if walls[cell_nb] % 2 == 0:
        return False
    else:
        return True


def orientation_to_direction(orientation, left, front, right):
    north, west, south, east = 0, 0, 0, 0
    if orientation == 1:
        west = left
        north = front
        east = right
    elif orientation == 2:
        west = front
        north = right
        south = left
    elif orientation == 3:
        west = right
        south = front
        east = left
    elif orientation == 4:
        north = left
        east = front
        south = right

    return north, west, south, east


def write_cell_walls(pos_x, pos_y, orientation):
    if was_visited(pos_x, pos_y):
        pass
    else:
        cell_byte = 0x01  # starting from 1, because cell is being visited now
        left, front, right = read_walls(pos_x, pos_y, orientation)
        north, west, south, east = orientation_to_direction(
            orientation, left, front, right
        )
        if east:
            cell_byte = cell_byte + 2
        if south:
            cell_byte = cell_byte + 4
        if west:
            cell_byte = cell_byte + 8
        if north:
            cell_byte = cell_byte + 16

        walls[cell_position_to_number(pos_x, pos_y)] = cell_byte


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


def turn(orientation, turn_dir):
    if turn_dir == "right":
        print("is turning right")
        print(orientation)
        if orientation != 4:
            print("New orientation: {}".format(orientation + 1))
            return orientation + 1
        else:
            return 1
    elif turn_dir == "left":
        print("is turning right")
        if orientation != 1:
            return orientation - 1
        else:
            return 4
    else:
        pass


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


def are_all_cells_visited():
    for i in range(16):
        for j in range(16):
            if was_visited(i, j):
                continue
            else:
                return False
    return True


def update_state(pos_x, pos_y, orientation):
    state = b"S" + struct.pack("2B", pos_x, pos_y) + orientation_to_byte(orientation)
    state += b"F"
    state += struct.pack("256B", *numbers)
    state += b"F"
    state += struct.pack("256B", *walls)
    req.send(state)
    # print("Request send with state: {}".format(state))
    req.recv()


def test_labirynth(orientation):
    for i in range(16):
        for j in range(16):
            write_cell_walls(i, j, orientation)
            update_state(i, j, orientation)


# number informs about the distance of cpecific cell to the center
# numbers[0] - SW, numbers[15] - NW, numbers[240] - SE, numbers[255] - NE
numbers = list(range(256))

# walls
# 000NWSEP
# P - 1, E - 2, S - 4, W - 8, N - 16
# p tells if the cell was visited, N if there is wall in the north, W west, E east, and S - south
walls = [0] * 256

# starting point
pos_x = 0
pos_y = 0
orientation = 1

update_state(pos_x, pos_y, orientation)

# test_labirynth(1)

k = 300
while not are_all_cells_visited() and k != 0:
    write_cell_walls(pos_x, pos_y, orientation)
    left, front, right = read_walls(pos_x, pos_y, orientation)
    if right == 0:
        orientation = turn(orientation, "right")
    elif left == 0:
        orientation = turn(orientation, "left")
    elif front == 0:
        pass
    else:
        orientation = turn(orientation, "left")
        orientation = turn(orientation, "left")
    update_state(pos_x, pos_y, orientation)
    print(pos_x, pos_y, orientation_to_byte(orientation), end=", after turning: ")
    pos_x, pos_y = move(pos_x, pos_y, orientation)
    print(pos_x, pos_y, orientation_to_byte(orientation), end=", after moving: ")
    update_state(pos_x, pos_y, orientation)
    print(pos_x, pos_y, orientation_to_byte(orientation), end=",  Walls: ")
    print(read_walls(pos_x, pos_y, orientation))
    k = k - 1


print(walls)


# print(read_walls(2, 4, b"N"))

