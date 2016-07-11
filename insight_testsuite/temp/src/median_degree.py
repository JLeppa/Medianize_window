#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 15:45:54 2016

@author: leppaj

A program to calculate median degree of a venmo transaction graph.

The input data of the program are Venmo transactions in a venmo-trans.txt file,
with each line corresponding to one transaction between actor and target at the
time provided on the line. Reading the lines one by one from the file simulates
obtaining the data through Venmo's API.

The venmo graph consists of nodes, which are labeled by the username, and
edges, which are connections between the nodes. A transaction between two users
results to an edge between the nodes labeled by their usernames. A degree of a
node is the number of edges connected to that node. Nodes are not directed,
i.e., a transaction from 'X' to 'Y' does not result to a new edge, if an edge
already exists from a transaction from 'Y' to 'X'. Only transactions falling
within a 60 second (exclusive) time window from the most recent transaction
populate the graph, and edges are evicted as needed, when more recent
transactions occur, which changes the time window.

The edges are extracted as alphabetically ordered tuples, which solves the
issue of edges bein one directed. The edges are stored into a dictionary
'edges', with the edge tuples as keys and times corresponding to the edges as
values. This allows for quick assessment for existence of an edge and for quick
update of the edge time. As a drawback, all edges need to be checked when the
time window changes to know which need to be evicted.

The nodes are stored into a dictionary as keys, with the corresponding degrees
as the values. This allows for quick assessment for existence of a node and for
quick update of the node degree. As a drawback, all values need to be collected
and sorted when calculating the median degree.

This source code is assumed to be in a folder called 'src', which should be in
the same parent folder with folders 'venmo_input' and 'venmo_output'. The input
file, 'venmo-trans.txt', should be in the venmo_input folder and output file,
'output.txt', is written into the 'venmo_output', overwriting any previous
file with the same name.
"""


# %%
# Needed modules, classes and function are imported in this section

from os import path
from re import search
from datetime import datetime, timedelta
from statistics import median

# %%
# Functions called by main are defined in this section


def edge_from_str(line_str):
    """ Extract edge (target and actor of a transaction) and time.

    Keyword arguments:
    line_str -- tansaction line from which the values are extracted (string)

    Return:
    -- If time, target and actor are found, return list where first item is a
    tuple that includes target and actor in alphabetical order, and second
    item is transaction time as datetime.datetime object
    -- If any of time, target and actor are not found, return None

    Note:
    -- Time assumed to be exactly in format 'YYYY-MM-DDThh:mm:ssZ'
    -- Usernames are assumed to consist of characters [a-zA-Z0-9_-.:]
    -- The transaction line assumed to include info exactly in the format
    'created_time": "t", "target": "x", "actor": "y"}', where
    t, x and y are time, username of target and username of actor, respectively
    """
    extract = search(r'created_time\": \"(\w\w\w\w-\w\w-\w\wT\w\w:\w\w:\w\wZ)'
                     r'\", \"target\": \"([\w:.-]*)'
                     r'\", \"actor\": \"([\w:.-]*)', line_str)
    if extract:                     # Extraction successful
        target = extract.group(2)   # Username of target
        actor = extract.group(3)    # Username of actor
        if target and actor:        # Return edge if target and actor found
            time_str = extract.group(1)     # Transaction time
            # Make a datetime.datetime object of the transaction time
            time_obj = datetime(int(time_str[:4]), int(time_str[5:7]),
                                int(time_str[8:10]), int(time_str[11:13]),
                                int(time_str[14:16]), int(time_str[17:19]))
            # Return extracted values
            # -- Here username starting with capital is sorted before one
            # starting with non-capital, but order is irrelevant as long as
            # the two usernames are always in the same order
            return [tuple(sorted([target, actor])), time_obj]
        else:
            return None     # Return None if target and/or actor not found
    else:
        return None         # Return None if extraction unsuccessful

# %%
# Main function is defined in this section


def main():
    """ The main function operates in the following sequence:

    1) Initialize variables
    2) Open input and output files
    3) Read lines from input file until first edge is found and write output
    -- Edge is found when time, actor and target of transaction are all found
    4) Read the rest of the lines; update graph and write output as needed
    -- If edge is not found -> no update or output
    -- If edge outside of current window -> output written, no update
    -- If edge within current window -> that edge updated and output written
    -- If edge more recent than current window -> graph updated, including
    --   potential edge and node evictions, and output written
    5) Close the input and output files
    """

    # 1) Initialize variables
    median_degree = 0   # Median degree (zero as no nodes are in graph)
    time_window = 60    # Duration of the time window considered (seconds)

    # 2) Open input and output files
    src_path = (path.dirname(path.realpath(__file__)))  # Path to source code
    rel_path = r'venmo_input\venmo-trans.txt'   # Relative path to input file
    input_path = path.join(path.dirname(src_path), rel_path)    # Absolute path
    input_data = open(input_path, 'r')          # Open input data file
    rel_path = r'venmo_output\output.txt'       # Relative path to output file
    output_path = path.join(path.dirname(src_path), rel_path)   # Absolute path
    output = open(output_path, 'w')             # Open the output file
                                                # - Overwrites previous file!

    # 3) Read lines from input file until first edge is found
    while median_degree == 0:
        line = input_data.readline()    # Read new line
        extract = edge_from_str(line)   # Extract edge from new line
        if extract:                     # If edge was found:
            edge = extract[0]           # First edge
            time_obj = extract[1]       # Timestamp of first edge
            latest_time = time_obj      # Initialize latest time of time window
            edges = {edge: time_obj}    # Initialize dictionary with edges as
                                        #   keys and times as values
            nodes = {edge[0]: 1, edge[1]: 1}    # Initialize dictionary with
                                                #   node as the key and degree
                                                #   of the node as the value
            median_degree = 1.0         # Median degree is 1 (only 1 edge)
            #   Truncate the output to two decimals (no rounding)
            med_degree_str = '%.2f' % (int(median_degree*100)/100) + '\r\n'
            output.write(med_degree_str)  # Write median degree to output file

    # 4) Read the rest of the lines; update and output as needed
    for line in input_data:             # Loop through data lines one at a time
        extract = edge_from_str(line)   # Extract the edge of the new line
        if extract:                     # Actions taken only if edge is found
            edge = extract[0]           # Edge of the new line
            time_obj = extract[1]       # Time corresponding to new line
            #   Time difference between line time and latest time (s)
            time_dif = (time_obj-latest_time).total_seconds()

            # Three possible actions depending on the time difference:
            # A) New line later or same as current latest time
            # B) New line earlier than latest time, but within current window
            # C) New line earlier than current window

            # Case A) New line later or same as current latest_time
            if (time_dif >= 0.0):
                if edge in edges:           # If edge already exists:
                    edges[edge] = time_obj  #   Update the time of that edge
                else:                       # If edge is not in graph:
                    edges[edge] = time_obj  #   Add edge to the graph
                    for node in edge:       # Loop through nodes of the edge
                        if node in nodes:       # If node exist:
                            nodes[node] += 1    #   Increase node degree
                        else:                   # If node is new:
                            nodes[node] = 1     #   Add node with degree 1

                #   Evict edges and empty nodes as needed
                if time_dif > 0.0:          # Evict only if time window changes
                    latest_time = time_obj  # Update latest time
                    #   End time of the updated time window:
                    end_time = latest_time - timedelta(seconds=time_window)
                    #   List of edges that need to be evicted:
                    evict_edges = [edge for edge in edges
                                   if edges[edge] <= end_time]
                    if evict_edges:             # If edges need to be evicted
                        for edge in evict_edges:    # Loop through edges
                            edges.pop(edge)         #   Remove edge from graph
                            for node in edge:           # Loop through nodes
                                if nodes[node] == 1:    # If degree drops to 0
                                    nodes.pop(node)     #   Remove node
                                else:                   # Otherwise
                                    nodes[node] -= 1    #   Decrease degree

                #   Calculate the median degree from updated nodes
                median_degree = median(nodes.values())
                #   Truncate the output to two decimals without rounding
                med_degree_str = '%.2f' % (int(median_degree*100)/100) + '\r\n'
                output.write(med_degree_str)    # Write median degree to output

            # Case B) New line falls within current window
            elif (time_dif > -60):
                if edge in edges:               # If edge already exists
                    if edges[edge] < time_obj:  #   If new time more recent
                        edges[edge] = time_obj  #     Update time
                else:                           # If edge is not in graph:
                    edges[edge] = time_obj      #   Add edge to graph
                    for node in edge:           # Loop through nodes of edge
                        if node in nodes:           # If node exist:
                            nodes[node] += 1        #   Increase node degree
                        else:                       # If node is new:
                            nodes[node] = 1         #   Add node with degree 1
                    #   Calculate the median degree from updated nodes:
                    median_degree = median(nodes.values())
                #   Truncate the output to two decimals without rounding:
                med_degree_str = '%.2f' % (int(median_degree*100)/100) + '\r\n'
                output.write(med_degree_str)    # Write output

            # Case C) New line earlier than current window
            else:
                output.write(med_degree_str)    # Write output (no updates)

    # 5) Close the input and output files
    input_data.close()
    output.close()

# %%
# Boilerplate to call the main function

if __name__ == '__main__':
    main()
