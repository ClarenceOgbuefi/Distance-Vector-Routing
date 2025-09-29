# Distance Vector project for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, Jeffrey Randow, new VM fixes by Jared Scott and James Lohse.

from Node import *
from helpers import *

NEG_INF = -99

class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        """ Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here."""


        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        self.dv = {self.name: 0} # initializes table with one entry (self where cost to recah is 0)
        self.cost_to_neighbors = {} # Builds map os reachable neighbors and their cost to reach them
        # self.next_hop = {}
        for nb in self.outgoing_links: # Initial knowledge
            weight_int = int(nb.weight)
            self.cost_to_neighbors[nb.name] = weight_int
            self.dv[nb.name] = weight_int


    def send_initial_messages(self):
        """ This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight """

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py

        # Called initially to advertise distances to upstream neighbors
        if not self.neighbor_names:
            return
        msg = {"from": self.name, "vector": self.dv.copy()} # Felt it was better to captures snapshot using copy > solution for accidental mutations, etc.
        for upstream in self.neighbor_names:
            self.send_msg(msg, upstream)



    def process_BF(self):
        """ This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. """

        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:     
        # TODO 1. Takes snapshot of queue and empties it

        # Called every round to consume DV messages, perform Bellman-Ford Alg, and advertise updates to upstream neighbors
        changed = False
        inbox = self.messages # Snaptshot before clearing messages
        self.messages = []

        # TODO 2. Process each message
        for msg in inbox:

            if not isinstance(msg, dict) or 'from' not in msg or 'vector' not in msg:
                continue

            origin = msg["from"]
            vector = msg["vector"]

            if origin not in self.cost_to_neighbors:
                continue

            try:
                via_cost = int(self.cost_to_neighbors[origin]) # Cost to reach neighbor to be used as next hop (Issue at end with variable types so just casting to int)
            except (TypeError, ValueError):
                continue

            for dest, ncost in vector.items(): # Prevent from changing cost to self
                if dest == self.name:
                    if dest not in self.dv:
                        self.dv[dest] = 0
                    continue

                if ncost == NEG_INF or ncost == str(NEG_INF): # Handles issue of negative infinity (issue with variable type so changed so it accepts str and int)
                    if self.dv.get(dest) != NEG_INF:
                        self.dv[dest] = NEG_INF
                        changed = True
                    continue
     
                try:
                    ncost_int = int(ncost) # variable type fix
                except (TypeError, ValueError):
                    continue

                if ncost_int < NEG_INF: # Handles cases where cost is less than -99 
                    ncost_int = NEG_INF

                if self.dv.get(dest) == NEG_INF:
                    continue

                candidate = via_cost + ncost
                if candidate < NEG_INF: # Handles cases where cost is less than -99 
                    candidate = NEG_INF
                current = self.dv.get(dest)

                # if current == NEG_INF:
                #     continue

                if current is None or candidate < int(current): # updates if path to destination via origin has lower cost than current best
                    self.dv[dest] = candidate
                    changed = True

        # TODO 3. Send neighbors updated distances 
        if changed: # Advertises only upon changes
            out = {"from": self.name, "vector": self.dv.copy()}
            for upstream in self.neighbor_names:
                self.send_msg(out, upstream)

    def log_distances(self):
        """ This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:(A,0) (B,1) (C,-2)
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 """
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided.        
        # add_entry("A", "(A,0) (B,1) (C,-2)")    
        parts = [f"({self.name},0)"]  # self always 0
        for dest in sorted(self.dv.keys()):
            if dest == self.name:
                continue
            parts.append(f"({dest},{self.dv[dest]})")
        # line = " ".join(parts)
        add_entry(self.name, " ".join(parts))
