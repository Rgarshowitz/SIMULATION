import numpy as np
import heapq
import matplotlib.pyplot as plt
import math as mt

class Event():
    def __init__(self, time, type, destination=None, package=None):
        self.time=time
        self.type=type
        self.destination=destination
        self.package=package
        heapq.heappush(P,self)

    def __lt__(self,event2):
        return self.time < event2.time

class Package():
    def __init__(self, size, first_sending_option, destination, cur_location=None, bin_size=None, 
    is_priority=False, ft_sent=None, st_sent=None, days_in_center=0):
        self.size=size
        self.size=size
        self.first_sending_option=first_sending_option
        self.destination=destination
        self.cur_location=cur_location
        self.bin_size=bin_size
        self.is_priority=is_priority
        self.ft_sent=ft_sent
        self.st_sent=st_sent
        self.days_in_center=days_in_center

    def __lt__(self, package2):
        return self.first_sending_option < package2.first_sending_option

class Destination():
    def __init__(self, id, large_bins=4, medium_bins=6, small_bins=15, is_working=True, neighbors={"big":[],"medium":[],"small":[]}):
        self.id=id
        self.large_bins=large_bins
        self.medium_bins=medium_bins
        self.small_bins=small_bins
        self.is_working=is_working
        self.neighbors=neighbors

#Define Destinations
Dest1=Destination(1)
Dest1.neighbors["big"], Dest1.neighbors["medium"], Dest1.neighbors["small"]=[2,3,4],[4,2,3],[4,2,3]
Dest2=Destination(2)
Dest2.neighbors["big"], Dest2.neighbors["medium"], Dest2.neighbors["small"]=[1,4],[1,4],[1,4]
Dest3=Destination(3)
Dest3.neighbors["big"], Dest3.neighbors["medium"], Dest3.neighbors["small"]=[1,5,4],[4,1,5],[4,1,5]
Dest4=Destination(4)
Dest4.neighbors["big"], Dest4.neighbors["medium"], Dest4.neighbors["small"]=[1,5,2,6,3],[6,2,5,1,3],[6,2,5,1,3]
Dest5=Destination(5)
Dest5.neighbors["big"], Dest5.neighbors["medium"], Dest5.neighbors["small"]=[6,3,4],[6,4,3],[6,4,3]
Dest6=Destination(6)
Dest6.neighbors["big"], Dest6.neighbors["medium"], Dest6.neighbors["small"]=[5,4],[4,5],[4,5]

P=[]   #Event heap
NOW=0   #Current simulation time
simulation_time=91   #Overall simulation running time
F=0   #indicates weather it is the first day for the simulation
returned_num=0   #Number of packages that has been returned to the logistics center
returned_clients_num=0   # number of clients that had to come back later because of destination malfunction
packages_in_center={"big":{}, "medium":{}, "small":{}}   #Dictionary that counts how many packages are left each days in center by category
days_to_delivery={1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}   # Counts how much time passed for each package in center for each destination, by days

