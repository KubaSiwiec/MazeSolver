import brute_force as bf


# starting point definition
pos_x = 0
pos_y = 0
orientation = 1

# update state before the simulation starts
bf.update_state(pos_x, pos_y, orientation)


# maximum step number to avoid infinite loop
k = 0


while not bf.are_all_cells_visited() and k != 1800:

    bf.write_cell_walls(pos_x, pos_y, orientation)
    bf.update_state(pos_x, pos_y, orientation)

    are_there_walls = bf.read_walls(pos_x, pos_y, orientation)

    weights = bf.get_cell_weight(pos_x, pos_y, orientation)
    print(weights)

    orientation = bf.choose_where_to_turn(orientation, weights, are_there_walls)

    pos_x, pos_y = bf.move(pos_x, pos_y, orientation)
    bf.update_state(pos_x, pos_y, orientation)
    k = k + 1
    # time.sleep(0.1)
    print(k)


if bf.are_all_cells_visited():
    print("The robot has visited the whole labirynth in {} moves".format(k))
else:
    print("It is getting too long")
