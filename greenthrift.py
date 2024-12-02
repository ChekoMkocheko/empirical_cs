'''


Input: Appliances 𝑁 , Loads 𝐿, New Load L, Inflex Load Iˆ,
Carbon Intensity Cˆ, Energy Price Pˆ, Breaker peak load Bmax, 𝛼, 𝛽.
Output: Load start times 𝑆.
1: if 𝐿L.𝑖! = 𝜙 then ⊲ A load exist for this appliance.
2: 𝑑𝑖,1 ← 𝑙𝑖,1 ⊲ Schedule for now.
3: end if
4: L.𝑑 ← min(L.𝜆, L.𝑤) + L.𝑙
5: 𝐿.𝑎𝑝𝑝𝑒𝑛𝑑(L)
6: 𝑆 ← Solve Optimization(𝑁, 𝐿, Iˆ, Cˆ, Pˆ, Bmax, 𝛼, 𝛽)
7: return 𝑆



**************

Notation Description
𝑁 𝑁 = {0, 1, ..., 𝑛} is the set of appliances.
𝐿𝑖 𝐿𝑖 is the set of loads loads for appliance 𝑖 : 𝑖 ∈ 𝑁 .
𝑒𝑖,𝑗 Energy consumption per slot of the 𝑗-th load of appliance 𝑖.
𝑝𝑖,𝑗 Peak power consumption of the 𝑗-th load of appliance 𝑖.
𝑙𝑖,𝑗 Length of the 𝑗-th load of appliance 𝑖.
𝑎𝑖,𝑗 Arrival time of the 𝑗-th load of appliance 𝑖.
𝑑𝑖,𝑗 Deadline for the 𝑗-th load of appliance 𝑖.1
P𝑡 Price of electricity at time 𝑡.
C𝑡 Carbon intensity at time 𝑡.
𝛼 Carbon weight parameter.
𝛽 Cost weight parameter.
I𝑡 Inflexible load power consumption at time 𝑡.
Bmax Breaker peak load.
𝑠𝑖,𝑗,𝑡 load 𝑗 of appliance 𝑖 starts at time 𝑡.
𝑥𝑖,𝑗,𝑡 load 𝑗 of appliance 𝑖 is running at time 𝑡.
where, 𝑖 ∈ 𝑁 , 𝑗 ∈ 𝐿𝑖, and 𝑡 ∈ [1,𝑇 ].

**************




'''

def scheduler(N, L):
    print("This is my scheduler")
    start_times = {}
    # Check if a load exist for the appliance
    for appliance_id in N:
        if appliance_id in L and L[appliance_id]:
            print("Found a task")
            print(appliance_id)
            # Schedule for now 
        # Now find the best time to schedule the new load. 
    


    return 

def load_scheduling():
    return

def add_new_load(L, new_load):
    appliance_id = new_load.pop('appliance_id')
    if appliance_id in L:
        L[appliance_id].append(new_load)
    else:
        L[appliance_id] = [new_load]

def print_all_items(L):
    for appliance_id, loads in L.items():
        print(f"Appliance {appliance_id}:")
        for i, load in enumerate(loads, 1):
            print(f"  Load {i}:")
            for key, value in load.items():
                print(f"    {key}: {value}")
        print()  # Add a newline for readability between appliances



if __name__ == "__main__":

    # Set of appliances, N = {0, 1, ..., n}
    N = [0, 1, 2, 3]  # Two appliances (a washing machine and a dishwasher)
    L = {
        0: [  # Appliance 0 (e.g., Washing Machine)
                {'energy_consumption': 1.5, 'peak_power': 2.0, 'length': 2, 'arrival_time': 0, 'deadline': 5},
                {'energy_consumption': 1.0, 'peak_power': 1.5, 'length': 1, 'arrival_time': 3, 'deadline': 6}
            ],
        1: [  # Appliance 1 (e.g., Dishwasher)
            {'energy_consumption': 1.2, 'peak_power': 1.8, 'length': 2, 'arrival_time': 1, 'deadline': 7}
            ]
        }
    #print_all_items(L)
    newload = {'appliance_id': 0, 'energy_consumption': 0.8, 'peak_power': 1.3, 'length': 1, 'arrival_time': 2,'deadline': 6}
    add_new_load(L, newload)
    #print_all_items(L)
    carbon_intensity = [100, 120, 110, 90, 80, 70, 60]
    energy_price = [20, 18, 22, 17, 15, 19, 21]
    B_max = 5.0
    alpha = 0.7  # Carbon weight parameter
    beta = 0.3   # Cost weight parameter
    inflexible_load = [0.5, 0.7, 0.6, 0.4, 0.6, 0.5, 0.3]  # Power consumption in each time slot

    scheduler(N, L)


'''


{'energy_consumption': 1.5, 'peak_power': 2.0, 'length': 2, 'arrival_time': 0, 'deadline': 5}, = 2*1.5 = 3 --> 4
{'energy_consumption': 1.0, 'peak_power': 1.5, 'length': 1, 'arrival_time': 3, 'deadline': 6} = 1 * 1 = 1 -->1.5
{'energy_consumption': 1.2, 'peak_power': 1.8, 'length': 2, 'arrival_time': 1, 'deadline': 7} = 1.2 * 2 = 2.4 -->3.6
                                                                                                            == 6.4 total max draw
                                                                                                            == 9.1 total max draw



0***1***2***3***4***5***6**7***8
--------------------: 2
            ------------: 1
    -----------------------: 2

** Means find when inflexible loads are happening, calculate the available time. 
  ** Therefore create an energy profile of the house for the next 24 hours
  ** Get how much electricity is available for each hour, then use the infromation to 
  ** find the best time to perform the task given the constraints 

'''

