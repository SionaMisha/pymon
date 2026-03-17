

import random
import csv
import sys
from datetime import datetime


# Below defined classes are used to raise various exceptions that might occur during the code exceution
class InvalidDirectionException(Exception):
    """Exception for when a selected direction has no connecting location."""
    def __init__(self, message="There is no door in the specified direction.."):
        self.message = message
        super().__init__(self.message)
    pass

class InvalidInputFileFormat(Exception):
    """Exception for invalid or incorrectly formatted CSV input files."""
    def __init__(self, message="The input file format is invalid or contains incorrect content."):
        self.message = message
        super().__init__(self.message)
    pass

# function to handle the command line arguments
def initialize_game():
    # Default file names
    location_file = "locations.csv"
    creature_file = "creatures.csv"
    item_file = "items.csv"

    # Check for command-line arguments
    if len(sys.argv) > 1:
        location_file = sys.argv[1]
    if len(sys.argv) > 2:
        creature_file = sys.argv[2]
    if len(sys.argv) > 3:
        item_file = sys.argv[3]

    # Initialize Record object with given or default files
    record = Record(location_file, creature_file, item_file)

    return record

#Function to save the game in the csv file
def save_game(self, filename):
    # Open the CSV file in write mode
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Save locations
        writer.writerow(['Location Name', 'Description', 'West', 'North', 'East', 'South'])
        for location in self.locations.values():
            writer.writerow([location.name, location.description,
                             location.doors['west'], location.doors['north'],
                             location.doors['east'], location.doors['south']])

        # Save creatures
        writer.writerow(['Creature Name', 'Description', 'Adoptable'])
        for creature in self.creatures:
            writer.writerow([creature.nickname, creature.description, creature.can_be_adopted])


#Function to load  Game progress
def load_game(self, filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

        # Load locations (assuming the format follows the same structure as above)
        for row in rows[1:]:  # Skip header row
            name, description, west, north, east, south = row
            location = Location(name, description, west, north, east, south)
            self.locations[name] = location

        # Load creatures (assuming the format follows the same structure as above)
        for row in rows[len(self.locations) + 2:]:  # Skip the location rows and header
            nickname, description, can_be_adopted = row
            creature = Creature(nickname, description, can_be_adopted.lower() == 'yes')
            self.creatures.append(creature)

#For admin to add locations   
def add_location(self):
    name = input("Enter location name: ")
    description = input("Enter description: ")
    west = input("Enter west location or 'None': ")
    north = input("Enter north location or 'None': ")
    east = input("Enter east location or 'None': ")
    south = input("Enter south location or 'None': ")

    location = Location(name, description, west, north, east, south)
    self.locations[name] = location

    # Now save this new location to locations.csv
    with open("locations.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, description, west, north, east, south])

#for admin to add creatures
def add_creatures(self):
    nickname = input("Enter creature nickname: ")
    description = input("Enter description: ")
    can_be_adopted = input("Can this creature be adopted? (yes/no): ").strip().lower()
    
    creature_type = input("Is this a Pymon or Animal? (Pymon/Animal): ").strip().lower()
    
    if creature_type == 'pymon':
        creature = Pymon(nickname, description, can_be_adopted == "yes")
    else:
        print("Creature is a animal")

    self.creatures.append(creature)

    # Save the new creature to creatures.csv
    with open("creatures.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nickname, description, can_be_adopted])

#Function for randomizing the connections between locations:
def randomize_location_connections(self):
    locations_list = list(self.locations.values())

    for location in locations_list:
        # Randomly assign new connections
        location.doors['west'] = random.choice(locations_list).name if random.random() > 0.5 else None
        location.doors['north'] = random.choice(locations_list).name if random.random() > 0.5 else None
        location.doors['east'] = random.choice(locations_list).name if random.random() > 0.5 else None
        location.doors['south'] = random.choice(locations_list).name if random.random() > 0.5 else None

        # Update the connections in the Location object (you might need to implement connect methods if they don't exist)
        if location.doors['west']:
            location.connect_west(self.locations[location.doors['west']])
        if location.doors['north']:
            location.connect_north(self.locations[location.doors['north']])
        if location.doors['east']:
            location.connect_east(self.locations[location.doors['east']])
        if location.doors['south']:
            location.connect_south(self.locations[location.doors['south']])


# Helper function for random generation
def generate_random_number(max_number=1):
    return random.randint(0, max_number)


class Creature:
    def __init__(self, nickname, description, can_be_adopted=False):  
        self.nickname = nickname
        self.description = description
        self.can_be_adopted = can_be_adopted
        self.location = None    

class Pymon(Creature):
    def __init__(self, name="Kimimon"):
        super().__init__(name, "black and white Pymon with a triangle face")   
        self.energy = 3
        self.current_location = None
        self.inventory = []
        self.creature_list = []
        self.battle_history = []  # Store battle results here
        self.move_count = 0
        self.immunity = False  # For magic potion immunity


    def move(self, direction=None):
        if self.current_location:
            if self.current_location.doors.get(direction):
                new_location = self.current_location.doors[direction]
                new_location.add_creature(self)
                self.current_location.creatures.remove(self)
                self.current_location = new_location
                print(f"{self.nickname} travelled {direction}and arrived at {self.current_location.name}")
                self.move_count += 1
                # Reduce energy every 2 moves
                if self.move_count % 2 == 0:
                    self.energy -= 1
                    print(f"{self.nickname}'s energy decreased to {self.energy}/3.")
                    
                    # Check if energy is depleted
                    if self.energy == 0:
                        print(f"{self.nickname} has fainted and escaped to the wild!")
                        self.spawn(random.choice(list(self.current_location.doors.values())))
            else:
                print(f"There is no door to the {direction}. Pymon remains at the current location")

    def spawn(self, location):
        if location:
            location.add_creature(self)  # add creature to location
            self.current_location = location

    def pick_item(self, item_name):
        found_item = False
        for item in self.current_location.items:
            if item.name.lower() == item_name.lower() and item.can_be_picked:
                self.inventory.append(item)   #Add item to inventory
                self.current_location.items.remove(item)    #Remove item from inventory
                print(f"{self.nickname} picked up {item.name}.")
                found_item = True
                break
        if not found_item:
            print(f"{item_name} cannot be picked up or is not present here.")
            pickable_items = [item for item in self.current_location.items if item.can_be_picked]
            if pickable_items:
                print("Items available to pick up:")
                for item in pickable_items:
                    print(f"- {item.name}: {item.description}")
            else:
                print("No items available to pick up at this location.")  

     # function to view the added items             
    def view_inventory(self):
        if self.inventory:
            print("Inventory:")
            for item in self.inventory:
                status = "used" if item.is_used else "unused"
                print(f"- {item.name} ({status})")
        else:
            print("Inventory is empty.")

    #use item function
    def use_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower() and not item.is_used:
                if item.use_effect == "energy" and self.energy < 3:
                    self.energy += 1
                    print(f"{self.nickname} ate an apple. Energy is now {self.energy}/3.")
                    item.is_used = True
                elif item.use_effect == "immunity":
                    self.immunity = True
                    print(f"{self.nickname} used a magic potion and now has immunity.")
                    item.is_used = True
                
                elif item.use_effect == "binoculars":
                    direction = input("View surroundings in which direction (current, west, north, east, south)?: ").lower()
                    self.view_surroundings(direction)
                    item.is_used = True
                return
        print(f"{item_name} cannot be used or is already used.")



    def view_surroundings(self,direction):
     #Provides a detailed view in a selected direction or current location description.
        if direction == "current":
            print(f"Current surroundings at {self.current_location.name}:")
            for creature in self.current_location.creatures:
                print(f"- {creature.nickname}: {creature.description}")
            for item in self.current_location.items:
                print(f"- {item.name}: {item.description}")
        elif direction in ["north", "south", "east", "west"]:
            next_location = self.current_location.doors.get(direction)
            if next_location:
                print(f"In the {direction} lies {next_location.name} - {next_location.description}.")
                # Optionally, add creatures and items in the next location
                for creature in next_location.creatures:
                    print(f"- {creature.nickname}: {creature.description}")
                for item in next_location.items:
                    print(f"- {item.name}: {item.description}")
            else:
                print(f"This direction leads nowhere.")
        else:
            print("Invalid direction selected.")

    # challenging the opponent
    def challenge(self, creature_name):

        # Try finding the opponent
        opponent = next((creature for creature in self.current_location.creatures
                        if creature.nickname.lower() == creature_name.lower() and creature.can_be_adopted), None)
        
        if opponent:
            print(f"{opponent.nickname} gladly accepted your challenge! Ready for battle")
            # print(f"Challenging {opponent.nickname}!")
            print("The first Pymon to win 2 of encounters will win the battle")
            self.battle(opponent)
        else:
            print(f"Challenge is invalid. Either no Pymon named '{creature_name}' here, or it's not adoptable.")
            print("Available creatures for challenging are:")
            for creature in self.current_location.creatures:
                print(f"{creature.nickname} ")

    #save the battle details
    def log_battle(self, opponent_name, pymon_wins, draws, opponent_wins):
        # Get current date and time
        battle_time = datetime.now().strftime("%d/%m/%Y %I:%M%p")
        
        # Log battle statistics
        self.battle_history.append({
            "timestamp": battle_time,
            "opponent": opponent_name,
            "wins": pymon_wins,
            "draws": draws,
            "losses": opponent_wins
        })

    # the rock paper scissor battle
    def battle(self, opponent):
        shapes = ["rock", "paper", "scissor"]
        pymon_wins = 0
        opponent_wins = 0
        draws = 0
        # encounters = 0

        while pymon_wins < 2 and opponent_wins < 2 and self.energy > 0:
            pymon_choice = input("Choose your shape (rock, paper, scissor): ").lower()
            print(f"You chose: {pymon_choice}")
            if pymon_choice not in shapes:
                print("Invalid choice. Try again.")
                continue

            opponent_choice = random.choice(shapes)
            print(f"Opponent chose: {opponent_choice}")  #opponents choice

            if pymon_choice == opponent_choice:
                draws +=1
                print(f"{pymon_choice} vs {opponent_choice}: Draw, no one wins this encounter.")
            elif (pymon_choice == "rock" and opponent_choice == "scissor") or \
                 (pymon_choice == "paper" and opponent_choice == "rock") or \
                 (pymon_choice == "scissor" and opponent_choice == "paper"):
                pymon_wins += 1
                print(f"{pymon_choice} vs {opponent_choice}: You won {pymon_wins} encounter")
            else:
                opponent_wins += 1
                if self.immunity:
                    print(f"{self.nickname} is immune to losing energy this round.")
                    self.immunity = False
                else:
                    self.energy -= 1
                    print(f"{pymon_choice} vs {opponent_choice}:You lost 1 encounter and 1 energy")
                

        #checking who wins
        if pymon_wins > opponent_wins:
            print(f"Congrats! You have won the battle and adopted a new Pymon called {opponent.nickname}!")
            self.creature_list.append(opponent)
        else:
            print("Sorry! You lost the battle.")
            if self.energy == 0:
                print("Your Pymon has fainted and is returned to the wild.")
                self.current_location.creatures.remove(self)
                self.spawn(random.choice(list(self.current_location.doors.values())))

         # Log the battle with the outcome
        self.log_battle(opponent.nickname, pymon_wins, draws, opponent_wins)

    #display stats
    def display_battle_stats(self):
        total_wins, total_draws, total_losses = 0, 0, 0
        print(f"\nBattle History for {self.nickname}:")

        for i, battle in enumerate(self.battle_history, 1):
            print(f"Battle {i}, {battle['timestamp']} Opponent: {battle['opponent']}, "
                  f"W: {battle['wins']} D: {battle['draws']} L: {battle['losses']}")
            total_wins += battle['wins']
            total_draws += battle['draws']
            total_losses += battle['losses']

        print(f"\nTotal: W: {total_wins} D: {total_draws} L: {total_losses}")


class Item:
    def __init__(self, name, description, can_be_picked=True, use_effect=None):
        self.name = name
        self.description = description
        self.can_be_picked = can_be_picked
        self.use_effect = use_effect
        self.is_used = False

class Location:
    def __init__(self, name, description):    #should be initialise the w=None in the defination 
        self.name = name
        self.description = description
        self.doors = {"west": None, "north": None, "east": None, "south": None}
        self.creatures = []
        self.items = []

    def add_creature(self, creature):
        creature.location = self
        self.creatures.append(creature)


    def add_item(self, item):
        self.items.append(item)


    def connect(self, direction, other_location):
        self.doors[direction] = other_location
        opposite = {"west": "east", "east": "west", "north": "south", "south": "north"}
        other_location.doors[opposite[direction]] = self


class Record:
    def __init__(self,location_file="locations.csv", creature_file="creatures.csv", item_file="items.csv"):
        self.pymon = Pymon()
        self.locations = {}
        self.creatures = []
        self.items = []

    # Load data from files
        self.import_locations(location_file)
        self.import_creatures(creature_file)
        self.import_items(item_file)

    def import_locations(self,filename):
        try:
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    # Skip empty rows or rows with missing data
                    if len(row) < 2:
                        continue
                    
                    # Extract location name and description
                    name, description = row[0], row[1]
                    
                    # Parse directional connections if they exist
                    doors = {}
                    for door in row[2:]:
                        if "=" in door:
                            direction, connected_name = door.split('=')
                            doors[direction.strip()] = connected_name.strip()
                    
                    location = Location(name, description)
                    self.locations[name] = (location, doors)

            # Connect locations based on doors
            for location, doors in self.locations.values():
                for direction, connected_name in doors.items():
                    if connected_name != "None" and connected_name in self.locations:
                        location.connect(direction, self.locations[connected_name][0])
        except FileNotFoundError:
            print(f"Error: {filename} not found.")

   

    def import_creatures(self, filename):
        try:
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                
                # Load all creatures from the CSV file into a list
                creatures = []
                for row in reader:
                    nickname, description, can_be_adopted = row[0], row[1], row[2].strip().lower() == "yes"
                    creature = Creature(nickname, description, can_be_adopted)
                    creatures.append(creature)
                
                # Convert the locations dictionary to a list of Location objects for easier indexing
                locations_list = [loc[0] for loc in self.locations.values()]

                #  Ensure at least one creature in each location
                for location in locations_list:
                    if creatures:
                        creature = creatures.pop(0)  # Assign the first creature to each location
                        location.add_creature(creature)
                        self.creatures.append(creature)
                    else:
                        print("Not enough creatures to assign at least one to each location.")
                        return  # Exit if there are not enough creatures

                # Randomly distribute remaining creatures
                for creature in creatures:
                    random_location = random.choice(locations_list)
                    random_location.add_creature(creature)
                    self.creatures.append(creature)
                    
        except FileNotFoundError:
            print(f"Error: {filename} not found.")   
    
    def import_items(self,filename):
        try:
            with open(filename, mode="r") as file:
                reader = csv.reader(file)
                
                # Convert locations dictionary to a list of Location objects
                locations_list = [loc[0] for loc in self.locations.values()]

                # Create a list to hold items, to later assign at least one item to each location
                items = []

                # Read each item from CSV and create an Item object
                for row in reader:
                    if len(row) < 2:
                        print(f"Skipping row due to incorrect format: {row}")
                        continue  # Skip rows with incorrect format
                    
                    item_name, description = row[0], row[1]
                    item = Item(item_name, description, can_be_picked=True)
                    items.append(item)  # Add the item to the list of items

                # Now assign at least one item to each location
                for location in locations_list:
                    if items:
                        # Pop an item from the list and add it to the current location
                        item = items.pop()
                        location.add_item(item)

                # After assigning at least one item to each location, distribute any remaining items
                for item in items:
                    # Randomly assign any leftover items to random locations
                    random_location = random.choice(locations_list)
                    random_location.add_item(item)

                print("All items have been assigned to locations, with at least one item per location.")
        
        except FileNotFoundError:
            print(f"Error: {filename} not found")

#All main opertaions are here in the class opertaion
class Operation:
    def __init__(self):
        self.record = Record()
        self.pymon = Pymon()

    # initial setup
    def setup(self):
        self.record.import_locations('locations.csv')
        self.record.import_creatures('creatures.csv')
        self.record.import_items('items.csv')
        random_location = random.choice(list(self.record.locations.values()))[0]
        self.pymon.spawn(random_location)  # Spawn Pymon at the random location
        print(f"Pymon starts at: {random_location.name}")

    def menu(self):
        while True:
            print("1. Start Game")
            print("2. Load Game")
            print("3. Save Game")
            print("4. Admin Mode")
            print("5. Quit")

            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.start_game()
            elif choice == "2":
                filename = input("Enter the save file name: ")
                self.load_game(filename)
            elif choice == "3":
                filename = input("Enter the save file name: ")
                self.save_game(filename)
            elif choice == "4":
                self.admin_menu()  # Go to admin menu
            elif choice == "5":
                break
            else:
                print("Invalid choice, please try again.")
    #Admin menu
    def admin_menu(self):
        while True:
            print("1. Add Custom Location")
            print("2. Add Custom Creature")
            print("3. Randomize Location Connections")
            print("4. Back to Main Menu")
            
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.add_location()
            elif choice == "2":
                self.add_creatures()
            elif choice == "3":
                self.randomize_location_connections()
            elif choice == "4":
                break
            else:
                print("Invalid choice, please try again.")
    #players menu
    def handle_menu(self):
        while True:
            print("\nPlease issue a command to your Pymon:")
            print("1) Inspect Pymon")
            print("2) Inspect current location")
            print("3) Move")
            print("4) Pick an item")
            print("5) View inventory")
            print("   a. Select item to use")
            print("6). Challenge a creature")
            print("7) Generate stats")
            print("8) Exit the program")
            choice = input("Choose an option: ")
            
            if choice == "1":
                self.inspect_pymon()
            elif choice == "2":
                self.inspect_location()
            elif choice == "3":
                self.move_pymon()
            elif choice == "4":
                item_name = input("Enter the name of the item to pick: ")
                self.pymon.pick_item(item_name)
            elif choice == "5":
                self.pymon.view_inventory()
                sub_choice = input("Do you want to use an item? (y/n): ")
                if sub_choice.lower() == 'y':
                    item_name = input("Enter the name of the item to use: ")
                    self.pymon.use_item(item_name)
            elif choice == "6":
                creature_name = input("Enter the creature to challenge: ")
                self.pymon.challenge(creature_name)
            elif choice == "7":
                self.pymon.display_battle_stats()
            elif choice == "8":
                print("Exiting the program.")
                break
            else:
                print("Invalid choice. Please try again.")

    #inspect pymon
    def inspect_pymon(self):
        print("\n1. Inspect current Pymon")
        print("2. Select a benched Pymon")
        choice = input("Select an option: ")
        if choice == "1":
            print(f"Name: {self.pymon.nickname}")
            print(f"Description: {self.pymon.description}")
            print(f"Energy: {self.pymon.energy}/3")
        elif choice == "2" and self.pymon.creature_list:
            print("Select a Pymon from your pet list:")
            for idx, pymon in enumerate(self.pymon.creature_list):
                print(f"{idx + 1}. {pymon.nickname}")

            selection = int(input("Enter choice: ")) - 1

            if 0 <= selection < len(self.pymon.creature_list):
                new_pymon = self.pymon.creature_list.pop(selection)
                self.pymon.creature_list.append(self.pymon)
                self.pymon = new_pymon
                print(f"{self.pymon.nickname} is now your active Pymon!")
            else:
                print("Invalid choice.")
        else:
            print("No Pymons in your pet list.")

    def inspect_location(self):
        loc = self.pymon.current_location
        print(f"You are at {loc.name}, {loc.description}.")
        if loc.creatures:
            print("Creatures in this location:")
            for creature in loc.creatures:
                print(f"- {creature.nickname}: {creature.description}")
        else:
            print("No creatures are here")
        
        print("Items:")
        if loc.items: # check is there are any items at the location
            for item in loc.items:
                print(f"- {item.name}: {item.description}")
        else: 
            print("No items are here.")

#Move pymon to different location
    def move_pymon(self):
        direction = input("Moving to which direction(west, north, east,south)?: ").strip().lower()
        if direction in ["west", "north", "east", "south"]:
            self.pymon.move(direction)
        else:
            print("Invalid direction. Please choose west, north, east, or south.")
    
    def pick_item(self):
        item_name = input("Enter the name of the item to pick: ")
        self.pymon.pick_item(item_name)


   #Start game
    def start_game(self):
        print("Welcome to Pymon World!")
        self.setup()
        print(f"\nYou started at {self.pymon.current_location.name}")
        self.handle_menu()

if __name__ == '__main__':
    ops = Operation()
    ops.menu()



# Design Reflection and Analysis
    
# Initial Design
# In this project, the goal was to simulate a creature management game with multiple locations, creatures, and items. I approached the design by breaking the system into clear components:

# Locations: Each location has a name, description, and possible connections (doors) to other locations.
# Creatures: Creatures can be of two types: Pymon and Animal. They have attributes such as nickname, description, and whether they can be adopted.
# Items: Items can be found at different locations, and each item has specific properties (e.g., whether it can be picked up or used).
    
# Game Logic: The game needs to manage interactions between creatures, locations, and items, and also handle game state saving/loading.
    
# Development Process
# I started by defining classes for Location, Creature, and Item to represent the main game entities. After that, I focused on creating methods for reading data from CSV files (using csv.reader), which allowed me to import and save game data (e.g., creatures, locations, items). This approach ensured that data could be easily loaded and saved in a structured manner.
# A key decision I made was to use randomization for creature and item placement. This adds variability to the game, making it more unpredictable. For instance, when importing creatures, I assigned them random locations to increase replayability.

# Challenges
# One challenge I encountered was ensuring that data for creatures and locations was properly linked, especially when assigning random locations. Initially, I had trouble handling the locations being stored as tuples, which caused errors when trying to call methods on them (such as add_creature). I solved this by ensuring that I was accessing the actual Location object, not just the tuple that was returned by the dictionary.

# Another challenge was the need to randomize the connections between locations for gameplay unpredictability. To solve this, I implemented a system where each location would be assigned random connections on startup, and certain sides (e.g., west, north, east, south) could be None to signify no door exists.

