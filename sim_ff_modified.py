import flood_fill_modified as ffm


# flood fill functions
def distances_calculated(numbers):
    for i in range(len(numbers)):
        if i in (119, 120, 135, 136):
            # center of the maze, distance is 0, countinue then
            continue
        else:
            if numbers[i] == 0:
                return False
    return True


# starting point definition
pos_x = 0
pos_y = 0
orientation = 1

# update state before the simulation starts
ffm.update_state(pos_x, pos_y, orientation)


# maximum step number to avoid infinite loop
k = 0
last_visited = []

while not ffm.is_in_the_center(pos_x, pos_y):

    ffm.write_cell_walls(pos_x, pos_y, orientation)
    ffm.update_state(pos_x, pos_y, orientation)

    are_there_walls = ffm.read_walls(pos_x, pos_y, orientation)

    weights = ffm.get_cell_weight(pos_x, pos_y, orientation)
    # print(weights)

    min_neighbour = ffm.should_update_numbers(pos_x, pos_y, weights, are_there_walls)
    if min_neighbour:
        ffm.numbers[ffm.cell_position_to_number(pos_x, pos_y)] = min_neighbour + 1
        for i in last_visited:
            p_x, p_y = ffm.cell_number_to_position(i)
            weights = ffm.get_cell_weight(p_x, p_y, orientation)
            min_neighbour = ffm.should_update_numbers_dir_based(p_x, p_y)
            if min_neighbour:
                ffm.numbers[ffm.cell_position_to_number(p_x, p_y)] = min_neighbour + 1
                # ffm.update_state(pos_x, pos_y, orientation)
            else:
                continue

    orientation = ffm.choose_where_to_turn(orientation, weights, are_there_walls)

    last_visited.insert(0, ffm.cell_position_to_number(pos_x, pos_y))

    pos_x, pos_y = ffm.move(pos_x, pos_y, orientation)
    ffm.update_state(pos_x, pos_y, orientation)
    k = k + 1
    # time.sleep(0.1)
    # print(k)


print("The robot has found the center in {} moves".format(k))


# Robot nie zawsze wybiera skręt w kierunku najniższej wagi, można spróbować wybór skrętu po kierunku, a nie po orientacji robota
