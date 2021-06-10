# Necesary imports to run the code
import csv
import sys
import random
import datetime 
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import figure
from networkx import nx
import numpy as np

# Change YOURPATH to the path where the airport routes dataset is
routes = "/YOURPATH/Dataset.csv"

# Read the csv file and return the origin and destination from it
def readMyFile(routes):
    origin = []
    destination = []

    with open(routes) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            origin.append(row[0])
            destination.append(row[1])

    return origin, destination    

# Calls the above method to read the file and save the retun into the origin and destination variables
origin, destination  = readMyFile(routes)

# We create a networkX graph called G
# We initialize it with the origin and destination from before
G = nx.Graph()
for i in range(len(origin)):
  if origin[i] == "Source" or destination == "Target":
    continue
  else:  
    G.add_edge(origin[i], destination[i])
    G.add_edge(destination[i], origin[i])


# Initialise nodes with attributes
for airport in G.nodes():
  attrs = {airport: {"infected": False, "closed": False, "dateInfected": "", "dataClosed": ""}}
  nx.set_node_attributes(G, attrs)

# Resets the date stored in every node when re-run to prevent problems
def resetData():
  for airport in G.nodes():
    if G.nodes[airport]["infected"] == True or G.nodes[airport]["closed"] == True:
      reset = {airport: {"infected": False, "closed": False, "dateInfected": "", "dataClosed": ""}}
      nx.set_node_attributes(G, reset)

# Search for the airport code (e.g. WHU) and return the object
def GetAirportNode(code):
  for airport in G.nodes():
    if airport == code:
      return airport

# Search the airport code (e.g. WHU) and return an array of the destinations from that airport
def GetDestinations(code):
  destinations = []
  for edge in G.edges(code):
    destinations.append(edge[1])
  return destinations

# Will return an airport infection status when given the code (e.g. WHU)
def GetInfected(code):
  return G.nodes[code]["infected"]

# Will return an airport closure status when given the code (e.g. WHU)
def GetClosed(code):
  return G.nodes[code]["closed"]

# Given the code (e.g. WHU) and a date it will set an airport as infected
def SetDateInfected(code, date):
  G.nodes[code]["dateInfected"] = currentDate[0]
  G.nodes[code]["infected"] = True
  if code not in infectedAirportsCodes:
    infectedAirportsCodes.append(code)  

# Given the code (e.g. WHU) it will set an airport as closed
def SetAirportClosed(code):
  G.nodes[code]["closed"] = True
  G.nodes[code]["dateClosed"] = currentDate[0]
  if code not in closedAirportsCodes:
    closedAirportsCodes.append(code)

# Checks the status of all the airport nodes and decides if we should close them based on the threshold (closeThreshold)
def shouldWeCloseAirport():
  airportsClosedToday = []
  for airport in G.nodes():
    currentAirport = G.nodes[airport]
    numberOfDestinationInfected = 0 #counter for infected neighbours
    destinations = GetDestinations(airport)
    for destination in destinations:
      if G.nodes[destination]["infected"] == True:
        numberOfDestinationInfected += 1
      percentageDestInfected = numberOfDestinationInfected / len(destinations) #calculates the % of the direct neighbours
      if percentageDestInfected > closeThreshold and G.nodes[airport]["closed"] == False: #if percentage is beyond threshold we close airport
        SetAirportClosed(airport)
        airportsClosedToday.append(airport) #add it to closed airports list
  return airportsClosedToday

# This updates all the nodes that are infected together at the end of each day 
def UpdateInfections(airportsInfectedToday):
  for i in range(len(airportsInfectedToday)):
    SetDateInfected(code = airportsInfectedToday[i], date = currentDate[0])

# This is the main function which is responsible for the infection of the airports and all the steps required
# It will run for as many days until it is equal to the targetDate
# Creates 2 arrays airportsInfectedToday, airportsClosedToday to store all the number of infected airports in a specific day
# Goes through all the airport nodes. If the node is infected, then we can proceed to infect more destinations nodes from that airport
# For every destination in the destinations list, we will get a random float number between 0 and 1 to check against the infectionRate treshold
# We check if the destination airport is not infected and not closed in order to infect it
# The counterMax will be increased by 1 in order to infect a maximum of 3 airports as the doctors research show
def infectAirport():
  while currentDate[0] <= targetDate:
    airportsInfectedToday = []
    airportsClosedToday = []
    for airport in G.nodes():
      if G.nodes[airport]["infected"] == True:
        counterMax = 0
        destinations = GetDestinations(airport)
        for destination in destinations:
          if random.random() <= infectionRate and counterMax < maxNumberOfInfectedPerAirportPerDay: 
            # we randomly generate a number and check if it is lower than infectionRate
            # this will choose approximately the percentage of airports defined in infectionRate
            # if neighbour not infected nor closed, we can infect
            if GetInfected(destination) == False and GetClosed(destination) == False: 
              counterMax += 1
              airportsInfectedToday.append(destination) # add to the airports closed today
    airportsClosedToday = shouldWeCloseAirport() # will check if we should close any airports and return the list of them if any
    print("Infected airports today: ")
    print(airportsInfectedToday)        
    UpdateInfections(airportsInfectedToday) # calls to update the airports and set their atributes
    print("Closed airports today:")
    print(airportsClosedToday)
    print("Number of infected airports today: {}".format(len(airportsInfectedToday)))
    print("Number of airports closed today: ",len(airportsClosedToday))
    print("Number of infected airports overall: {}".format(len(infectedAirportsCodes)))
    print("Number of closed airports overall: {}".format(len(closedAirportsCodes)))
    print("END OF THE DAY: {}" .format(currentDate[0].strftime("%d %b %Y")))
    print("")


    # data appended to generate graphs
    graph_date.append(currentDate[0].strftime("%d.%m.%Y"))
    graph_daily_infections.append(len(airportsInfectedToday))
    graph_total_infections.append(len(infectedAirportsCodes))
    graph_daily_closure.append(len(airportsClosedToday))
    graph_total_closure.append(len(closedAirportsCodes))

    # reset the variable and increase the current date to move to next day
    airportsClosedToday = []
    currentDate[0] += datetime.timedelta(days=1)


# ---------- START -----------
# The program starts here by setting Wuhan as the first airport to be infected
# Sets the infection date on the 31 as the first infection day, and start infection others from 1.1.2020
sourceOfVirus = "WUH"
currentDate = [datetime.datetime(2019,12,31)]
infectedAirportsCodes = []
closedAirportsCodes = []

# Reseting previous data for Google Colab
resetData()

# Treshholds of the simulation and end date for the simulation
infectionRate = 0.1
maxNumberOfInfectedPerAirportPerDay = 3
closeThreshold = 0.75
targetDate = datetime.datetime(2020,5,15) # Date Format: Year,Month,Day

# Creating the variables for the chart data
graph_date = []
graph_daily_infections = []
graph_total_infections = []
graph_daily_closure = []
graph_total_closure = []

# Infecting the first city Wuhan and starting the simulation
SetDateInfected("WUH", currentDate)
# After wuhan was infected in first day, we move to the next day
currentDate[0] += datetime.timedelta(days=1)
infectAirport()

# An overview of the total number of infected and closed airports at the end of the simulation
print("Total number of airports infected: " + str(len(infectedAirportsCodes)))
print("Total number of airports closed: " + str(len(closedAirportsCodes)))

# Creating the grath and sizing it
fig, ax = plt.subplots(figsize=(8,4)) # change the interes in figsize() to resize the graph

# Adding data to the grapth. Comment any of the plots to remove the line
thickness = 2 # change the thickness of the lines
ax.plot(graph_date, graph_daily_infections, label = "Infections per day", linewidth=thickness)
ax.plot(graph_date, graph_total_infections, label = "Infection overall", linewidth=thickness)
ax.plot(graph_date, graph_daily_closure, label = "Closures per day", linewidth=thickness)  
ax.plot(graph_date, graph_total_closure, label = "Closure overall", linewidth=thickness) 

# naming the x axis 
plt.xlabel('Date') 

# naming the y axis 
plt.ylabel('Number of Infections/Closure') 

# giving a title to my graph 
plt.title('Infections and Closure Overtime \n Infection Rate: {0} | Closure Threshold: {1} \n Simulation Period: 01.01.2020 --> {2}'.format(infectionRate,closeThreshold,targetDate.strftime("%d.%m.%Y"))) 

# show a legend on the plot
plt.legend(loc='upper right', bbox_to_anchor=(1.0, 0.9)) # delete bbox_to_anchor to keep the legend automatic

# changing the scale of the x ticks at the bottom
ax.xaxis.set_major_locator(ticker.MaxNLocator(13))
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
plt.xticks(rotation=30) # rotate the bottom lables n degrees for a better fit

# function to show the plot
plt.show()


# ------------------------ TASK 4 ONLY -------------------------------
# installs necessary libaries for Task 4 & imports the necesary functions
!pip install ndlib
!pip install pyviz

import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
from bokeh.io import output_notebook, show
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend

model = ep.ThresholdModel(G)

# Model Configuration
config = mc.Configuration()
# This will set the initial fraction of infected nodes(airports)
# So 0.25 means that 25% of the nodes will be infected before we start infecting others
config.add_model_parameter('fraction_infected', 0.1)

# Setting node parameters
# Threshold for cascading, eg. if it is 0.1 then only 10% of neighbours is needed to get infected
threshold = 0.1
for i in G.nodes():
    config.add_node_configuration("threshold", i, threshold)

model.set_initial_status(config)

# Simulation execution
# Run the simulation for 10 iterations
iterations = model.iteration_bunch(10)
trends = model.build_trends(iterations)

# Create a DiffusionTrend model in order to allow us to plot graph
viz = DiffusionTrend(model, trends)
viz.plot("output.pdf") # save graph