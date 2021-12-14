import numpy as np
import heapq
import matplotlib.pyplot as plt
import math as mt
import pandas as pd

class Event():#EVENT CLASS
    def __init__(self, time, name, destination=None, package=None):
        self.time = time
        self.type = name
        self.destination = destination
        self.package = package
        heapq.heappush(P, self)

    def __lt__(self, event2):
        return self.time < event2.time

    def __repr__(self):
        if self.type == "Arrival":
            return f'{self.time} - Arrival'
        elif self.type == "Distribute":
            return f'{self.time} - distribution'
        elif self.type == "Collection":
            return f'{self.time} - package {self.package.size} collected from {self.destination}'
        elif self.type == "End Location Fault":
            return f'{self.time} - {self.destination} fixed'
        elif self.type == "Collect After Fault":
            return f'{self.time} - package collected after fault from {self.destination}' 
        elif self.type == "Missed Collection":
            return f'{self.time} - package returned beacuse of lazy client' 

class Package():  #package class
    def __init__(self, size, first_sending_option, destination):
        self.size = size                  #size of package 
        self.first_sending_option = first_sending_option   
        self.second_sending_option = None # when package returns to center
        self.destination = destination    # original destination
        self.cur_location = None          # actual location 
        self.bin_size = None              # size of bin that package is in
        self.is_priority = False          # has been returned to center 
        self.ft_sent = None               # first time package was sent
        self.st_sent = None               # second time packaeg was sent
        self.days_in_center = 0           # total day in logistical center
        self.current_time_in_bin = 0      # current time in bin

    def __repr__(self):
        return f'size: {self.size} destination:{self.destination.id} first_sending_option:{self.first_sending_option}'

    def __lt__(self, package2):           # used to decide which package is more urgant to send
        if self.is_priority==True:    
            return self.second_sending_option < package2.second_sending_option
        else:
            return self.first_sending_option < package2.first_sending_option

    def push_to_heap(self):               # packages are kept in priority heap
        if self.is_priority == True:
            heapq.heappush(vip_heap_dict[(self.destination.id, self.size)], self)
        else:
            heapq.heappush(regular_heap_dict[(self.destination.id, self.size)], self)
            
    def update_time_in_bin(self,time):    # when cleint comes to pick up package this is updated
        if self.is_priority:
            self.current_time_in_bin = time - self.st_sent
        else:
            self.current_time_in_bin = time - self.ft_sent
            
    def update_package_days_in_center(self,time): #when package is placed in bin this is updated
        if self.is_priority == False:
            self.ft_sent = time           
            self.days_in_center = mt.floor(self.ft_sent - self.first_sending_option)
        else:
            self.st_sent = time            
            self.days_in_center += mt.floor(self.st_sent - self.second_sending_option)

    

class Destination():   
    def __init__(self, id):
        self.id = id
        self.available_bins = {1: 4, 2: 6, 3: 15}
        self.is_working = True
        self.neighbors = {"big": [], "medium": [], "small": []}

    def __repr__(self):
        return f'loc ID:{self.id} L:{self.available_bins[1]} M:{self.available_bins[2]} S:{self.available_bins[3]}, is working: {self.is_working}'


#### sub Funcitons ####
def add_x_packages_to_heap(first_sending_option, i, j, x):  # subfunction that adds x packages to heap (i,j)
    t = 0
    while t < x:
        Package(j, first_sending_option, destinations[i]).push_to_heap()
        t += 1
    return None

def insert_to_bin(destination, package, bin_size, NOW):     # subfunction that "inserts" package to a specific bin
    destination.available_bins[bin_size] -= 1               # updates bin availability 
    package.bin_size = bin_size                             # updates what size bin packages is in
    package.cur_location = destination.id                   # updates the actual location of the package
    package.update_package_days_in_center(NOW)              # updates how long package has been in center
    package_collection_creation(package, NOW)               # creates package collection event


def update_days_to_delivery(package):                       # updates dict for madad 1
    if package.days_in_center in days_to_delivery[package.destination.id].keys():
        days_to_delivery[package.destination.id][package.days_in_center] += 1
    else:
        days_to_delivery[package.destination.id][package.days_in_center] = 1


def next_point(i, j):                # reacurring subfunction that helps move through heaps
    if j == 3:
        if i == 6:
            i += 1
            return (i, j)
        else:
            i += 1
            j = 1
            return (i, j)
    else:
        j += 1
        return (i, j)


def simple_placing(cur_pack, NOW):   # function that attemps to place pack in neighbor
    size_count = cur_pack.size
    while size_count-1 >= 0:
        neighbors = destinations[cur_pack.destination.id].neighbors[size_count]
        for i in neighbors:          # goes through relevent neigbors and finds suitible bin
            if destinations[i].available_bins[size_count] > 0:
                insert_to_bin(destinations[i], cur_pack, size_count, NOW)
                return False
        size_count -= 1
    if cur_pack.cur_location==None:  # if unseccuesful package is returned to center
        cur_pack.push_to_heap()
        return True


def place_pack(heap, curr_point, cur_dest,NOW):  # function that decides how to place package in original dest
    cur_pack = heapq.heappop(heap[(curr_point[0], curr_point[1])])
    if cur_pack.is_priority:
        if cur_pack.second_sending_option > NOW:
            cur_pack.push_to_heap()
            curr_point = next_point(curr_point[0], curr_point[1])   #go to next heap
            return curr_point  
    if cur_dest.available_bins[curr_point[1]] > 0:
        insert_to_bin(cur_dest, cur_pack, curr_point[1], NOW)
    elif curr_point[1]-1 >= 1:                                # Am I small/Medium
        if curr_point[1]-2 >= 1:                              # Am I small?
            if cur_dest.available_bins[curr_point[1]-1] > 0:  # are there medium bins available?
                insert_to_bin(cur_dest, cur_pack, curr_point[1]-1, NOW)
                return curr_point
            elif cur_dest.available_bins[curr_point[1]-2] > 0: # are there big bins available?
                insert_to_bin(cur_dest, cur_pack, curr_point[1]-2, NOW)
                return curr_point
            else:
                cur_pack.push_to_heap()
                curr_point = next_point(curr_point[0], curr_point[1])   #go to next heap
                return curr_point
        else:                                                  # are there big bins available?
            if cur_dest.available_bins[curr_point[1]-1] > 0:
                insert_to_bin(cur_dest, cur_pack, curr_point[1]-1, NOW)
                return curr_point
            else:                                              # There are no big bins available
                cur_pack.push_to_heap()
                curr_point = next_point(curr_point[0], curr_point[1]) #go to next heap
                return curr_point
    else:
        cur_pack.push_to_heap()
        curr_point = next_point(curr_point[0], curr_point[1])
    return curr_point

## [size][package_amount] = num of days that this amount of packages in center

def update_packages_in_center():
    global packages_in_center
    for j in range(1, 4):
        total_packages = 0
        for i in range(1, 7):
            total_packages += len(regular_heap_dict[i, j]) + len(vip_heap_dict[i, j])
        if total_packages in packages_in_center[j].keys():
            packages_in_center[j][total_packages] += 1
        else:
            packages_in_center[j][total_packages] = 1


### main functions ####
def package_arrival_creation(NOW):  #  Creates packages arrival event
    Event(mt.ceil(NOW), "Arrival")


def package_arrival_execution(NOW):  # Create daily packages arrival by destination
    for i in range(1, 7):
        for j in range(1, 4):
            x = np.random.poisson(loc_size_destributions[(i, j)])
            global packages_arrived
            if NOW == 0:
                add_x_packages_to_heap(NOW, i, j, x)
            else:
                if (NOW+1)%7 == 0:
                    add_x_packages_to_heap(NOW+1, i, j, x)
                else:
                    add_x_packages_to_heap(NOW, i, j, x)
    if NOW%7 == 0:
        if NOW!=0:
            return
    send_packages_creation(NOW)


def send_packages_creation(NOW):     # creates package distibution event
    Event(NOW+6/24, "Distribute")

def send_packages_execution(NOW, sending_method): # send packages according to method 1 or 2
    if sending_method==1:
        send_packages_1(NOW)
    else:
        send_packages_2(NOW)
    package_arrival_creation(NOW)

def send_packages_1(NOW):       #sending method 1 
    if mt.ceil(NOW)%7==0:
        send_packages_creation(mt.ceil(NOW))
        update_packages_in_center()
        return
    curr_point = (1, 1)  # (i,j)
    while curr_point[0] < 7:
        cur_dest = destinations[curr_point[0]]
        if len(vip_heap_dict[(curr_point[0], curr_point[1])]) > 0:
            curr_point = place_pack(vip_heap_dict, curr_point, cur_dest,NOW)
        elif len(regular_heap_dict[(curr_point[0], curr_point[1])]) > 0:
            curr_point = place_pack(regular_heap_dict, curr_point, cur_dest,NOW)
        else:
            curr_point = next_point(curr_point[0], curr_point[1])
    update_packages_in_center()

def send_packages_2(NOW):       # sending method 2
    send_packages_1(NOW)        #first of all tries to do sending method 1
    if mt.ceil(NOW)%7==0:
        return
    i, j = 1, 1
    while i < 7:
        move = True
        if len(regular_heap_dict[i, j]) > 0:
            cur_pack = heapq.heappop(regular_heap_dict[i, j])
            move=simple_placing(cur_pack, NOW)
        if move==True:
            if j==3:
                if i == 6:
                    i += 1
                else:
                    i += 1
                    j = 1
            else:
                j+=1
           

def package_collection_creation(package, NOW):    # pickup creation according too 
    x, y = np.random.uniform(0, 1), np.random.uniform(0, 17.983/24)
    if package.destination.id == package.cur_location:
        if x < 0.4:
            Event(NOW+y, "Collection", package.destination, package)
        elif x < 0.6:
            Event(NOW+1+y, "Collection", package.destination, package)
        elif x < 0.9:
            Event(NOW+2+y, "Collection", package.destination, package)
        else:
            Event(NOW+3+y, "Collection", package.destination, package)
    else:
        if x < 0.2:
            Event(NOW+y, "Collection", package.cur_location, package)
        elif x < 0.4:
            Event(NOW+1+y, "Collection", package.cur_location, package)
        elif x < 0.7:
            Event(NOW+2+y, "Collection", package.cur_location, package)
        elif x < 0.9:
            Event(NOW+3+y, "Collection", package.cur_location, package)
        else:
            missed_collection_creation(NOW,package)
         

def package_collection_execution(NOW, package):
    package.update_time_in_bin(NOW)
    if destinations[package.cur_location].is_working == True:
        x = np.random.uniform(0, 1)
        if x > 0.01:
            destinations[package.cur_location].available_bins[package.bin_size] += 1
            update_days_to_delivery(package)
            global packages_collected
            return
        else:
            w = np.random.uniform(1/24, 5/24)
            destinations[package.cur_location].is_working = False
            end_location_fault_creation(NOW +w, destinations[package.cur_location])
            global count_faults
            count_faults += 1

    if package.is_priority == True:
        global returned_clients_for_priority_packs
        collect_after_fault_creation(NOW, package)
        return
    elif mt.ceil(package.current_time_in_bin) > 4:
        global returned_num
        global returned_packs_due_to_fault
        package.is_priority = True
        returned_num += 1
        if mt.ceil(NOW+1)%7 == 0:
            package.second_sending_option = mt.ceil(NOW)+1
            package.push_to_heap()
        else:
            package.second_sending_option = mt.ceil(NOW)
            package.push_to_heap()
        return
   
    else:
        global returned_clients_for_regular_packs
        collect_after_fault_creation(NOW, package)
        return

def missed_collection_creation(NOW, package):
    Event(NOW+4, "Missed Collection", package.cur_location, package)

def missed_collection_execution(NOW,package):
    if mt.ceil(NOW+1)%7==0:
        package.second_sending_option = mt.ceil(NOW)+1
    else:
        package.second_sending_option = mt.ceil(NOW)
    destinations[package.cur_location].available_bins[package.bin_size] += 1
    package.is_priority = True
    package.push_to_heap()
    global returned_num
    global returned_packs_due_to_lazy_client
    returned_num +=1
  
def end_location_fault_creation(NOW, destination):
    t = np.random.uniform(1/24, 5/24)
    Event(NOW+t, "End Location Fault", destination)


def end_location_fault_excecution(destination):
    destination.is_working = True


def collect_after_fault_creation(NOW, package):
    y = np.random.uniform(6/24, 23.983/24)
    Event(mt.ceil(NOW)+y, "Collect After Fault", destinations[package.cur_location], package)


def collect_after_fault_execution(NOW, package):
    global returned_clients_num
    returned_clients_num += 1
    package_collection_execution(NOW, package)

returned_clients_num = 0
returned_num = 0
packages_in_center = {1: {}, 2: {}, 3: {}}  # Dictionary that counts how many packages are left each days in center by size
days_to_delivery = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}  # Counts how much time passed for each package in center for each destination, by days

number_of_simulations  = 50 

for Qsim in range(number_of_simulations):
    vip_heap_dict = {}
    for i in range(1, 7):
        for j in range(1, 4):
            vip_heap_dict[i, j] = []
    regular_heap_dict = {}
    for i in range(1, 7):
        for j in range(1, 4):
            regular_heap_dict[i, j] = []
    destinations = {}
    for i in range(1, 7):
        destinations[i] = Destination(i)
    # Define Destinations neigbors
    destinations[1].neighbors[1], destinations[1].neighbors[2], destinations[1].neighbors[3] = [2, 3, 4], [4, 2, 3], [4, 2, 3]
    destinations[2].neighbors[1], destinations[2].neighbors[2], destinations[2].neighbors[3] = [1, 4], [1, 4], [1, 4]
    destinations[3].neighbors[1], destinations[3].neighbors[2], destinations[3].neighbors[3] = [1, 5, 4], [4, 1, 5], [4, 1, 5]
    destinations[4].neighbors[1], destinations[4].neighbors[2], destinations[4].neighbors[3] = [1, 5, 2, 6, 3], [6, 2, 5, 1, 3], [6, 2, 5, 1, 3]
    destinations[5].neighbors[1], destinations[5].neighbors[2], destinations[5].neighbors[3] = [6, 3, 4], [6, 4, 3], [6, 4, 3]
    destinations[6].neighbors[1], destinations[6].neighbors[2], destinations[6].neighbors[3] = [4, 5], [4, 5], [4, 5]
    count_faults = 0
    P = []  # Event heap
    NOW = 0  # Current simulation time
    simulation_time = 91  # Overall simulation running time
    loc_size_destributions = {(1, 1): 1,  (1, 2): 3, (1, 3): 7,
                            (2, 1): 1.5, (2, 2): 2, (2, 3): 8,
                            (3, 1): 2,  (3, 2): 4, (3, 3): 12,
                            (4, 1): 3,  (4, 2): 1, (4, 3): 5,
                            (5, 1): 1,  (5, 2): 3, (5, 3): 8,
                            (6, 1): 1.5, (6, 2): 1, (6, 3): 3}
    Event(NOW, "Arrival")
    while NOW < 91:
        cur_event = heapq.heappop(P)
        NOW = cur_event.time
        if cur_event.type == "Arrival":
            package_arrival_execution(NOW)
        elif cur_event.type == "Distribute":
            send_packages_execution(NOW,2)
        elif cur_event.type == "Collection":
            package_collection_execution(NOW, cur_event.package)
        elif cur_event.type == "End Location Fault":
            end_location_fault_excecution(cur_event.destination)
        elif cur_event.type == "Collect After Fault":
            collect_after_fault_execution(NOW, cur_event.package)
        elif cur_event.type == "Missed Collection":
            missed_collection_execution(NOW,cur_event.package)
    for i in range(1,7):
        for j in range(1,4):
            while len(vip_heap_dict[i,j]) > 0:
                pack1 = heapq.heappop(vip_heap_dict[i,j])
                pack1.update_package_days_in_center(simulation_time)
                update_days_to_delivery(pack1)
            while len(regular_heap_dict[i,j]) > 0:
                pack2 = heapq.heappop(regular_heap_dict[i,j])
                pack2.update_package_days_in_center(simulation_time)
                update_days_to_delivery(pack2)
fig  = plt.gcf()
fig = fig.set_size_inches(10, 10)
fig , axs = plt.subplots(3, 3,figsize=(15,15))
axs[0, 0].bar(pd.Series(packages_in_center[1]).sort_index().keys(),height=pd.Series(packages_in_center[1]).sort_index().values/number_of_simulations,color = "r")
axs[0, 0].set_title('Large Packages in Center')
axs[0, 1].bar(pd.Series(packages_in_center[2]).sort_index().keys(),height=pd.Series(packages_in_center[2]).sort_index().values/number_of_simulations,color = "g")
axs[0, 1].set_title('Medium Packages in Center')
axs[0, 2].bar(pd.Series(packages_in_center[3]).sort_index().keys(),height=pd.Series(packages_in_center[3]).sort_index().values/number_of_simulations,color = "b")
axs[0, 2].set_title('Small Packages in Center')
axs[1, 0].bar(pd.Series(days_to_delivery[1]).keys(),height=pd.Series(days_to_delivery[1]).sort_index().values/number_of_simulations)
axs[1, 0].set_title("destination 1 days to delivery")
axs[1, 1].bar(pd.Series(days_to_delivery[2]).keys(),height=pd.Series(days_to_delivery[2]).sort_index().values/number_of_simulations)
axs[1, 1].set_title("destination 2 days to delivery")
axs[1, 2].bar(pd.Series(days_to_delivery[3]).keys(),height=pd.Series(days_to_delivery[3]).sort_index().values/number_of_simulations)
axs[1, 2].set_title("destination 3 days to delivery")
axs[2, 0].bar(pd.Series(days_to_delivery[4]).keys(),height=pd.Series(days_to_delivery[4]).sort_index().values/number_of_simulations)
axs[2, 0].set_title("destination 4 days to delivery")
axs[2, 1].bar(pd.Series(days_to_delivery[5]).keys(),height=pd.Series(days_to_delivery[5]).sort_index().values/number_of_simulations)
axs[2, 1].set_title("destination 5 days to delivery")
axs[2, 2].bar(pd.Series(days_to_delivery[6]).keys(),height=pd.Series(days_to_delivery[6]).sort_index().values/number_of_simulations)
axs[2, 2].set_title("destination 6 days to delivery")


for j in range(3):
    axs[0,j].set( xlabel= "Amount of Packages",ylabel= "days")
for i in range(1,3):
    for j in range(3):  
        axs[i,j].set( ylabel= "Amount of Packages",xlabel= "days")
        
fig.tight_layout()
                    
print(f'mean returned clients due to location fault: {returned_clients_num/number_of_simulations}')
print(f'mean packages returned to center:{returned_num/number_of_simulations}')
print(f'mean distribution location fails:{count_faults/number_of_simulations}')



