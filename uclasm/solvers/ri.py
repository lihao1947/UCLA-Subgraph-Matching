import re

def run_RI(tmplt, world, iso_type, input_format):
    """
    This will run the RI solver on the specified template and world graph.
    The remaining arguments adjust the operation of the LAD solver.

    Args:
        tmplt (Graph): The template graph
        world (Graph): The world graph
        iso_type (str): One of 'iso', 'ind', or 'mono' for graph isomorphism,
            induced subgraph isomorphism, and subgraph isomorphism respectively
        input_format (str): One of the following:
            'gfd': directed graph with node attributes
            'gfu': undirected graph with node attributes
            'ged': directed graph with node and edge attributes
            'geu': undirected graph with node and edge attributes
            Currently, only gfd is supported. Each of these are described at
            https://github.com/InfOmics/RI
    Returns:
        A 4-tuple, the first is the number of isomorphisms found, second is number of bad nodes,
        third is number of nodes searched, 4th is the time taken
    """

    # We need to create temporary files 
    tmp_tmplt_filename = tmplt.name + '.txt'
    tmp_world_filename = world.name + '.txt'

    # Currently only gfd will be supported
    if input_format == 'gfd':
        tmplt.write_file_gfd(tmp_tmplt_filename)
        world.write_file_gfd(tmp_world_filename)
    elif input_format == 'gfu':
        raise NotImplementedError
        tmplt.write_file_gfu(tmp_tmplt_filename)
        world.write_file_gfu(tmp_world_filename)
    elif input_format == 'ged':
        raise NotImplementedError
        tmplt.write_file_ged(tmp_tmplt_filename)
        world.write_file_ged(tmp_world_filename)
    elif input_format == 'geu':
        raise NotImplementedError
        tmplt.write_file_geu(tmp_tmplt_filename)
        world.write_file_geu(tmp_world_filename)
    else:
        raise ValueError("Unrecognized file type format: {}".format(input_format))

    command = "ri36 {} {} {} {}".format(iso_type, input_format, tmp_world_filename, tmp_tmplt_filename)

    # We store the printed output of the program into a StringIO
    output = subprocess.run(command, capture_output=True, shell=True)
    os.remove(tmp_tmplt_filename)
    os.remove(tmp_world_filename)
    return parse_output(output.stdout.decode())


def parse_output(output):
    key_value_pattern = "[^\n]*: (\S+)"
    values = re.findall(output)
    # The values should be in order: world file, template file, 
    # total time, match time, number of matches, search space size
    # We don't care about the filenames, so we don't return those
    return float(values[2]), float(values[3]), int(values[4]), int(values[5])
