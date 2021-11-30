import numpy as np
import heapq
import matplotlib.pyplot as plt
import math as mt
import pandas as pd

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
        self.first_sending_option=first_sending_option
        self.destination=destination
        self.cur_location=cur_location
        self.bin_size=bin_size
        self.is_priority=is_priority
        self.ft_sent=ft_sent
        self.st_sent=st_sent
        self.days_in_center=days_in_center

    def __repr__(self):
        return f'size: {self.size} destination:{self.destination.id} first_sending_option:{self.first_sending_option}'
    
    def __lt__(self, package2):
        return self.first_sending_option < package2.first_sending_option
    
    def push_to_heap(self):
        if self.is_priority == True:
            heapq.heappush(vip_heap_dict[(self.destination.id,self.size)],self)
        else:
            heapq.heappush(regular_heap_dict[(self.destination.id,self.size)],self)

class Destination():
    def __init__(self, id ):
        self.id=id
        self.available_bins = {1:4,2:6,3:15}
        self.is_working = True
        self.neighbors= {"big":[],"medium":[],"small":[]}
    def __repr__(self):
        return f'loc ID:{self.id} L:{self.available_bins[1]} M:{self.available_bins[2]} S:{self.available_bins[3]}, is working: {self.is_working}'


#### sub Funcitons ####
def add_x_packages_to_heap(NOW,i,j,x): #adds x packages to heap (i,j)
    t = 0
    while t<x:
        Package(j,NOW,destinations[i]).push_to_heap()
        t+=1
    return None

def insert_to_bin(cur_dest,cur_pack,i,j,NOW):
    cur_dest.available_bins[j] -= 1
    cur_pack.bin_size = j
    cur_pack.cur_location = i
    if cur_pack.is_priority:
        cur_pack.st_sent = NOW
        cur_pack.days_in_center += mt.floor(cur_pack.st_sent - cur_pack.first_sending_option)
    else:
        cur_pack.ft_sent = NOW
        cur_pack.days_in_center = mt.floor(cur_pack.ft_sent - cur_pack.first_sending_option)

def update_days_to_delivery(package):
    if package.days_in_center in days_to_delivery[package.destination.id].keys():
        days_to_delivery[package.destination.id][package.days_in_center]+=1
    else:
        days_to_delivery[package.destination.id][package.days_in_center]=1
        
        
def next_point(i,j):
    if j ==3:
        if i == 6:
            i+=1
            return (i,j)
        else:
            i += 1 
            j = 1
            return (i,j)
    else:
        j+=1
        return (i,j)
    
def place_pack(heap,curr_point,cur_dest):
    cur_pack = heapq.heappop(heap[(curr_point[0],curr_point[1])])

    if cur_dest.available_bins[curr_point[1]] > 0:
        insert_to_bin(cur_dest,cur_pack,curr_point[0],curr_point[1],NOW)
        #print(f'placed item size {curr_point[1]} in bin {curr_point[1]} at {cur_dest}')
        package_collection_creation(cur_pack, cur_pack.cur_location, NOW)

    elif curr_point[1]-1 >= 1:  #Am I small/Medium
        if curr_point[1]-2 >=1:  # Am I small?
            if cur_dest.available_bins[curr_point[1]-1] > 0:  # are there medium bins available?
                insert_to_bin(cur_dest,cur_pack,curr_point[0],curr_point[1]-1,NOW)
                package_collection_creation(cur_pack, cur_pack.cur_location, NOW)
                return curr_point
            elif cur_dest.available_bins[curr_point[1]-2] > 0:   # are there big bins available?
                insert_to_bin(cur_dest,cur_pack,curr_point[0],curr_point[1]-2,NOW)
                package_collection_creation(cur_pack, cur_pack.cur_location, NOW)
                return curr_point
            else:
                cur_pack.push_to_heap()
                curr_point = next_point(curr_point[0],curr_point[1])
                return curr_point
        else:   # I am mediumn
            if cur_dest.available_bins[curr_point[1]-1] > 0:   # are there big bins available?
                insert_to_bin(cur_dest,cur_pack,curr_point[0],curr_point[1]-1,NOW)
                package_collection_creation(cur_pack, cur_pack.cur_location, NOW)
                return curr_point
            else: #There are no big bins available
                cur_pack.push_to_heap()
                curr_point = next_point(curr_point[0],curr_point[1])
                return curr_point        
    else:  
        cur_pack.push_to_heap()
        #print(f' done with ({curr_point})')
        curr_point = next_point(curr_point[0],curr_point[1])
        #print(f' next point:({curr_point})')

    return curr_point

def update_packages_in_center():
    global packages_in_center
    for j in range(1,4):
        total_packages=0
        for i in range(1,7):
            total_packages+=len(regular_heap_dict[i,j])+len(vip_heap_dict[i,j])
        if total_packages in packages_in_center[j].keys():
            packages_in_center[j][total_packages]+=1
        else:
            packages_in_center[j][total_packages]=1
        print(packages_in_center[j])
    

### main functions ####
def package_arrival_creation(NOW):
     Event(mt.ceil(NOW), "Arrival")

def package_arrival_execution(NOW): #Create daily packages
    for i in range(1,7):
        for j in range(1,4):
            x = np.random.poisson(loc_size_destributions[(i,j)])
            if F ==0:
                add_x_packages_to_heap(NOW,i,j,x)
            else:
                if NOW%7 == 0:
                    add_x_packages_to_heap(NOW+1,i,j,x)
                else:
                    add_x_packages_to_heap(NOW,i,j,x)
    send_packages_creation(NOW)
    print(f'time: {NOW} - Daily packages arrived')

def send_packages_creation(NOW):
    Event(NOW+6/24,"Distribute")

def send_packages_execution(NOW):
    curr_point = (1,1) # (i,j)
    while curr_point[0] < 7:
        cur_dest = destinations[curr_point[0]]
        if len(vip_heap_dict[(curr_point[0],curr_point[1])]) > 0:
            curr_point = place_pack(vip_heap_dict,curr_point,cur_dest)
        elif len(regular_heap_dict[(curr_point[0],curr_point[1])]) > 0:
            curr_point = place_pack(regular_heap_dict,curr_point,cur_dest)
        else:
            #print(f' done with ({curr_point})')
            curr_point = next_point(curr_point[0],curr_point[1])
            #print(f' next point:({curr_point})')
    update_packages_in_center()
    print(f'time: {NOW} - daily packages sent')
    package_arrival_creation(NOW)

def package_collection_creation(package,p_cur_location,NOW):
    x,y = np.random.uniform(0,1), np.random.uniform(0,17.983/24)
    if package.destination.id==p_cur_location:
        if x<0.4:
            Event(NOW+y,"Collection",package.destination,package)
        elif x<0.6:
            Event(NOW+1+y,"Collection",package.destination,package)
        elif x<0.9:
            Event(NOW+2+y,"Collection",package.destination,package)
        else:
            Event(NOW+3+y,"Collection",package.destination,package)
    else:
        if x<0.2:
            Event(NOW+y,"Collection",p_cur_location,package)
        elif x<0.4:
            Event(NOW+1+y,"Collection",p_cur_location,package)
        elif x<0.7:
            Event(NOW+2+y,"Collection",p_cur_location,package)
        elif x<0.9:
            Event(NOW+3+y,"Collection",p_cur_location,package)
        else:
            package.is_priority=False
            global returned_num
            if (NOW+5)%7==0:
                package.first_sending_option=mt.floor(NOW+6)
            else:
                package.first_sending_option=mt.floor(NOW+5)
            returned_num+=1
            package.push_to_heap()
              

def package_collection_execution(NOW,package):
    if package.destination.is_working==True:
        x=np.random.uniform(0,1)
        if x>0.01:
            destinations[package.destination.id].available_bins[package.bin_size]+=1
            if package.is_priority==False:
                update_days_to_delivery(package)
                print(f'{NOW}- package size {package.size} collected from loc {package.destination.id} bin size {package.bin_size}')

                return
        else:
            w=np.random.uniform(1/24,5/24)
            package.destination.is_working=False
            end_location_fault_creation(NOW,package.destination)
    if package.is_priority==True:
        collect_after_fault_creation(NOW,package)
        return
    elif ((NOW+1)-package.first_sending_option)<4:
        collect_after_fault_creation(NOW,package)
        return
    else:
        global returned_num
        package.is_priority=True
        if (NOW+1)%7==0:
            package.first_sending_option = mt.floor(NOW+2)
            returned_num+=1
            package.push_to_heap()
        else:
            package.first_sending_option = mt.floor(NOW+1)
            returned_num+=1
            package.push_to_heap()

def end_location_fault_creation(NOW,destination):
    t = np.random.uniform(1/24,5/24)
    Event(NOW+t, "End Location Fault", destination)

def end_location_fault_excecution(destination):
    destination.is_working = True

def collect_after_fault_creation(NOW,package):
    global returned_num
    y = np.random.uniform(6/24, 23.983/24)
    returned_num+=1
    Event(mt.ceil(NOW)+y, "Collect After Fault", package.cur_location, package)

def collect_after_fault_execution(NOW, package):
    global returned_clients_num
    returned_clients_num+=1
    package_collection_execution(NOW, package)


# create 18 package heaps in two dictionareis Vip and regular : the dict key is the heap name (i,j) value heap the 
vip_heap_dict = {}
for i in range(1,7):
    for j in range(1,4):
        vip_heap_dict[i, j] = []
regular_heap_dict = {}
for i in range(1,7):
    for j in range(1,4):
        regular_heap_dict[i, j] = []
destinations = {}
for i in range(1,7):
    destinations[i] = Destination(i)

#Define Destinations neigbors 
destinations[1].neighbors["big"], destinations[1].neighbors["medium"], destinations[1].neighbors["small"]=[2,3,4],[4,2,3],[4,2,3]
destinations[2].neighbors["big"], destinations[2].neighbors["medium"], destinations[2].neighbors["small"]=[1,4],[1,4],[1,4]
destinations[3].neighbors["big"], destinations[3].neighbors["medium"], destinations[3].neighbors["small"]=[1,5,4],[4,1,5],[4,1,5]
destinations[4].neighbors["big"], destinations[4].neighbors["medium"], destinations[4].neighbors["small"]=[1,5,2,6,3],[6,2,5,1,3],[6,2,5,1,3]
destinations[5].neighbors["big"], destinations[5].neighbors["medium"], destinations[5].neighbors["small"]=[6,3,4],[6,4,3],[6,4,3]
destinations[6].neighbors["big"], destinations[6].neighbors["medium"], destinations[6].neighbors["small"]=[4,5],[4,5],[4,5]

P=[]   #Event heap
NOW=0   #Current simulation time
simulation_time=91   #Overall simulation running time
F=0   #indicates weather it is the first day for the simulation
returned_num=0   #Number of packages that has been returned to the logistics center
returned_clients_num=0   # number of clients that had to come back later because of destination malfunction
packages_in_center={1:{}, 2:{}, 3:{}}   #Dictionary that counts how many packages are left each days in center by size
days_to_delivery={1:{}, 2:{}, 3:{}, 4:{}, 5:{}, 6:{}}   # Counts how much time passed for each package in center for each destination, by days
loc_size_destributions = {(1,1):1,  (1,2):3, (1,3):7,
                          (2,1):1.5,(2,2):2, (2,3):8,
                          (3,1):2,  (3,2):4, (3,3):12,
                          (4,1):3,  (4,2):1, (4,3):5,
                          (5,1):1,  (5,2):3, (5,3):8,
                          (6,1):1.5,(6,2):1, (6,3):3 } 

Event(NOW, "Arrival")
while NOW < 91:
    cur_event=heapq.heappop(P)
    NOW=cur_event.time
    if cur_event.type=="Arrival":
        package_arrival_execution(NOW)
    elif cur_event.type=="Distribute":
        send_packages_execution(NOW)
    elif cur_event.type=="Collection":
        package_collection_execution(NOW,cur_event.package)
    elif cur_event.type=="End Location Fault":
        end_location_fault_excecution(cur_event.destination)
    else:
        collect_after_fault_execution(NOW, cur_event.package)
