""" Matrix object to create the world """

import random
import statistics
from uuid import UUID
from typing import Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import psutil
from multiprocessing import Pool
import multiprocessing as mp
import panzoto.config as CFG
from panzoto.person import Person
from panzoto.child import Child
from panzoto.food import Food
from panzoto.utils import log_output, log, timer
from panzoto.enums import Logging, Gender, Stats


class Matrix():

    def __init__(self):
        self.people_dict = {}
        self.thing_dict = {}
        self.stats = {}

        # this is a list of dictionary values
        self.records = []
        # make sure turn starts at 0
        self.stats[Stats.TOTAL_TURNS.value] = 0

    @staticmethod
    def get_full_name(first_name: str,
                      last_name: str) -> str:
        """Generate the name of the person as a continous string

        Args:
            first_name (str): first name
            last_name (str): last name

        Returns:
            str: full name in continous string
        """
        return f'{first_name.capitalize()}_{last_name.capitalize()}'

    def create_person(self,
                      first_name: str = "anonymous",
                      last_name: str = "person") -> str:
        """create a person using first and last name

        Args:
            first_name (str): first name    
            last_name (str): last name

        Returns:
            str: all the output in from the function
        """

        output = ""

        person = Person(first_name, last_name)

        # loggin pref
        if CFG.person_messages:
            output += f'{person.name} created.'
        self.people_dict[person.uid] = person

        return output

    def create_people(self, 
                      total: str):
        output = ""
        for _ in range(int(total)):
            self.create_person(first_name="anonymous",
                               last_name="person")
        output += f"{total} people were created."

    def delete_person(self,
                      uid: str) -> str:
        """Remove a person from the matrix using uid string

        Args:
            uid (str): uuid string

        Returns:
            str: output from this function
        """

        output = ""

        try:
            uid = UUID(uid)
        except ValueError:
            log(text=f"Maybe try a valid uuid?",
                level=Logging.ERROR.value)
            return output

        if uid in self.people_dict:
            # output += f"{self.people_dict[uid].name} have been removed!"
            del self.people_dict[uid]
        else:
            output += 'That person does not exist!'

        return output

    def choose_parents(self) -> Tuple[Person, Person]:
        """Choose random mom and dad.

        Returns:
            Tuple[Person, Person]: Two person objects: mom and dad
        """

        male_list = []
        female_list = []
        
        # get a list of female and male UUIDs
        for key in self.people_dict:
            if self.people_dict[key].gender == Gender.FEMALE.value:
                female_list.append(key)
            elif self.people_dict[key].gender == Gender.MALE.value:
                male_list.append(key)
            else:
                log(text=f'Some gender are undefined',
                    level=Logging.ERROR.value)

        # choose a random set of parents if there is at least 1 from each
        if male_list and female_list:
            mom = random.choice(female_list)
            dad = random.choice(male_list)
            return self.people_dict[mom], self.people_dict[dad]
        else:
            log(text=f"Was not able to find a mom and a dad!",
                level=Logging.INFO.value)

    def create_child(self) -> str:
        """Create a child based on Child class settings

        Returns:
            str: output string
        """
        output = ""
        mom, dad = self.choose_parents()
        child = Child(mom=mom, dad=dad)
        self.people_dict[child.uid] = child

        return output

    @log_output
    def list_people(self) -> str:
        """List all the people in Matrix

        Returns:
            str: output string
        """
        output = ""
        if not self.people_dict:
            output += 'No people exist.'

        for person in self.people_dict:
            output += f'{self.people_dict[person].name}\n'

        return output

    @log_output
    def show_person(self,
                    first_name: str,
                    last_name: str) -> str:
        """Show info about a specific person

        Args:
            first_name (str): first name
            last_name (str): last name

        Returns:
            str: output of this function
        """
        output = ""
        name = self.get_full_name(first_name=first_name,
                                  last_name=last_name)
        target_list = [str(self.people_dict[x]) for x in self.people_dict
                       if name == self.people_dict[x].full_name]

        if target_list:
            output += "\n".join(target_list)
        else:
            output += f'Cannot find the person you are searching.'

        return output

    def assign_item(self,
                    thing_uid: str,
                    person_uid: str) -> str:
        """Assign an item to a person

        Args:
            thing_uid (str): item uid
            person_uid (str): person uid

        Returns:
            str: output string
        """

        output = ""

        thing_uid = UUID(thing_uid)
        person_uid = UUID(person_uid)

        # only assing item if both item and person exit
        if (person_uid in self.people_dict) and (thing_uid in self.thing_dict):
            person_object = self.people_dict[person_uid]
            thing_object = self.thing_dict[thing_uid]
            thing_object.owner = person_object.uid
            person_object.possession.append(thing_object)
            person_object.check_status()
            thing_object.check_status()
        # error messages if either peron or item doesn't exist
        elif (person_uid in self.people_dict) and \
            (thing_uid not in self.thing_dict):
            output += "That thing doesn't exist!"
        elif (person_uid not in self.people_dict) and \
            (thing_uid in self.thing_dict):
            output += "That person doesn't exist!"
        else:
            output += "Neither that person nor the thing exist!"

        return output

    def create_food(self,
                    name: str,
                    value: str) -> str:
        """Create a new food item

        Args:
            name (str): name of the food time
            value (str): how many times can the item be eaten

        Returns:
            str: output string
        """
        output = ""

        food = Food(name=name,
                    value=int(value))
        output += f'{food.name} created.'
        self.thing_dict[food.uid] = food

        return output

    @log_output
    def show_thing(self,
                   name: str) -> str:
        """Show info about a specific thing

        Args:
            name (str): name of item

        Returns:
            str: output of this function
        """
        output = ""
        name = name.capitalize()
        target_list = [str(self.thing_dict[x]) for x in self.thing_dict
                       if name == self.thing_dict[x].name]

        if target_list:
            output += "\n".join(target_list)
        else:
            output += f'Cannot find the thing you are searching.'

        return output

    @log_output
    def focus(self, *args) -> str:
        """Display stats about either a person or a thing

        Returns:
            str: output string 
        """
        output = ""
        if len(args) == 1:
            self.show_thing(*args)
        elif len(args) == 2:
            self.show_person(*args)
        else:
            output += "The thing to focus is neither a person or a thing."

    def remove_item_possession(self,
                               uid: UUID) -> str:
        """Remove the owner's possession of the given item

        Args:
            uid (UUID): uid of the thing for deletion

        Returns:
            str: output string
        """
        output = ""
        thing_object = self.thing_dict[uid]
        if thing_object.owner:
            owner_uid = thing_object.owner
            person = self.people_dict[owner_uid]
            person.possession.remove(thing_object)
            person.check_status()
        else:
            output += f"{thing_object.name} was not owned by anybody!"
        del self.thing_dict[uid]


        return output

    def delete_thing(self,
                     thing_id: str) -> str:
        """Remove a thing from the matrix

        Args:
            thing_id (str): uid of item

        Returns:
            str: output string
        """
        output = ""

        try:
            uid = UUID(thing_id)
        except ValueError:
            log(text=f"Maybe try a valid uuid?",
                level=Logging.ERROR.value)
            return output

        if uid in self.thing_dict:
            self.remove_item_possession(uid=uid)
        else:
            output += 'That thing does not exist!'

        return output

    @log_output
    def list_things(self) -> str:
        """List all the items in matrix

        Returns:
            str: output string
        """

        output = ""
        if not self.thing_dict:
            output += f"Nothing exisit yet."

        for thing in self.thing_dict:
            thing_object = self.thing_dict[thing]
            output += thing_object.name + "\n"

        return output

    @staticmethod
    def update_person(person: Person) -> Person:
        """Helper function for multiprocessing. no lambda :)

        Args:
            person (Person): peron object

        Returns:
            Person: return updated person object back after updating stats
        """
        person.run_one_turn()
        return person

    def check_people(self) -> str:
        """Update all the person object in maxtrix

        Returns:
            str: output string
        """
        output = ""

        # multiprocessing to spread out checking to multiple cores
        people = [self.people_dict[x] for x in self.people_dict]
        p = Pool(psutil.cpu_count())
        mp_results = p.map(self.update_person, people)

        for person in mp_results:
            # need to assign the values because the values from MP is no longer
            # linked to the original objects
            self.people_dict[person.uid] = person

            if not person.alive:
                self.delete_person(uid=person.uid.hex)
                
                # change log pref
                if CFG.person_messages:
                    output += f'{person.name} died.\n'

        return output

    def check_things(self) -> str:
        """Update all the item object in matrix

        Returns:
            str: output string
        """
        output = ""
        if not list(self.thing_dict):
            return output

        for key in list(self.thing_dict):
            item_object = self.thing_dict[key]

            if item_object.food_value <= 0:
                self.delete_thing(key.hex)
        return output

    def check_env(self):
        """This is all the setting of what's happening to the world
        1. birth rate 
        """
        birth_rate = CFG.birth_rate
        birth_number = self.stats[Stats.PEOPLE_COUNT.value] * birth_rate
        self.create_people(birth_number)

    def run_one_turn(self) -> None:
        """Calculate all the changes in one turn"""

        # keep track of total turns
        self.stats[Stats.TOTAL_TURNS.value] += 1

        self.check_people()
        self.check_things()
        self.update_stats()
        self.check_env()

        # save stats
        self.records.append(list(self.stats.values()))

    @log_output
    def run_n_turn(self,
                   num: int) -> None:
        """run n number of turns for a world simulation

        Args:
            num (int): number of iterations
        """
        output = ""
        output += f'Iter: {num} turns.'

        for i in range(int(num)):
            print(f"Turn: {i}")
            self.run_one_turn()

        return output

    def get_people_age_median(self) -> int:
        """Get the median of people age

        Returns:
            int: median of people age
        """

        total = [self.people_dict[x].age for x in self.people_dict]

        if not total:
            return 0
        else:
            median = statistics.median(total)
        return median

    def get_people_energy_median(self) -> int:
        """Get the median of people energy

        Returns:
            int: median of people energy
        """

        energy_total = [self.people_dict[x].energy for x in self.people_dict]
        
        if not energy_total:
            return 0
        else:
            median = statistics.median(energy_total)
        return median

    def get_people_health_median(self) -> int:
        """Get the median of people health

        Returns:
            int: median of people health
        """

        total = [self.people_dict[x].health for x in self.people_dict]
        if not total:
            return 0
        else:
            median = statistics.median(total)
        return median

    def get_female_count(self) -> int:
        """Count the number of female people

        Returns:
            int: femal count total
        """
        female_count = [x for x in self.people_dict 
                        if self.people_dict[x].gender == Gender.FEMALE.value]
        return len(female_count)

    def get_male_count(self) -> int:
        """Count the number of male people

        Returns:
            int: male count total
        """
        male_count = [x for x in self.people_dict
                        if self.people_dict[x].gender == Gender.MALE.value]
        return len(male_count)

    def update_stats(self) -> None:
        """Update the stats in self.Stats Dictionary
        1. total turns
        2. people count
        3. people energy median
        4. people health median
        5. item count
        6. female count
        7. male count
        """

        self.stats[Stats.PEOPLE_COUNT.value] = len(self.people_dict)
        self.stats[Stats.PEOPLE_AGE_MEDIAN.value] = \
            float(self.get_people_age_median())
        self.stats[Stats.PEOPLE_ENERGY_MEDIAN.value] = \
            float(self.get_people_energy_median())
        self.stats[Stats.PEOPLE_HEALTH_MEDIAN.value] = \
            float(self.get_people_health_median())
        self.stats[Stats.ITEM_COUNT.value] = len(self.thing_dict)
        self.stats[Stats.FEMALE_COUNT.value] = self.get_female_count()
        self.stats[Stats.MALE_COUNT.value] = self.get_male_count()


    @log_output
    def show_stats(self) -> str:
        """Generate stats as string

        Returns:
            str: stats string output
        """

        output = ""
        self.update_stats()

        for x in self.stats:
            output += f"{x}: {self.stats[x]}\n"

        return output

    @log_output
    def show_records(self) -> str:
        """Display all the records as string

        Returns:
            str: string output of all the records.
        """
        output = ""
        headers = [x.value for x in Stats]
        output += ",".join(headers) + "\n"
        for x in self.records:
            output += f"{x}\n"

        return output

    def graph_stats(self) -> None:
        """Generate graphs for stats over turns
        """
        stats = [x.value for x in Stats]
        data = pd.DataFrame(self.records, columns=stats)

        for stat in stats:
            # skip turn vs turn graph, not useful
            if stat == Stats.TOTAL_TURNS.value:
                continue

            sns_plot = sns.lineplot(data=data, 
                                    x=Stats.TOTAL_TURNS.value,
                                    y=stat)

            output_path = Path(CFG.default_matrix).parent \
                / CFG.graph_dir / f"{stat}.png"
            fig = sns_plot.get_figure()
            fig.savefig(output_path)
            plt.clf()
