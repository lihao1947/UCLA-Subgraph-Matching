"""
lad.py

This module will contain tools for running the LAD program
"""
import subprocess
import re
import os

def run_LAD(tmplt, world, timeout=60, stop_first=False, induced=False, enum=False, verbose=False):
    """
    This will run the LAD solver on the specified template and world graph.
    The remaining arguments adjust the operation of the LAD solver.

    Args:
        tmplt (Graph): The template graph
        world (Graph): The world graph
        timeout (int): The amount of time to run before quitting
        stop_first (bool): True if you want to stop after first isomorphism, False if you want to count
        induced (bool): True if you want induced subgraph isomorphism only
        enum (bool): True if you want to list all isomorphisms
        verbose (bool): True if you want verbose output, probably won't work
    Returns:
        A 4-tuple, the first is the number of isomorphisms found, second is number of bad nodes,
        third is number of nodes searched, 4th is the time taken
    """

    # We need to create temporary files 
    tmp_tmplt_filename = tmplt.name + '.txt'
    tmp_world_filename = world.name + '.txt'

    tmplt.write_file_solnon(tmp_tmplt_filename)
    world.write_file_solnon(tmp_world_filename)

    command = "lad -p {} -t {} -s {}".format(tmp_tmplt_filename, tmp_world_filename, timeout)
    if stop_first:
        command += " -f"
    if induced:
        command += " -i"
    if enum:
        command += " -v"
    if verbose:
        command += " -vv"

    # We store the printed output of the program into a StringIO
    output = subprocess.run(command, capture_output=True, shell=True)
    os.remove(tmp_tmplt_filename)
    os.remove(tmp_world_filename)
    return parse_output(output.stdout.decode())


def parse_output(output):
    return list(map(float, re.findall("[\d\.]+", output)))
