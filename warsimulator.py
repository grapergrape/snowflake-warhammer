from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import random
import polars as pl  

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RACE_LIST = ['Orc', 'CHAOS MARINES']
ORC_UNITS = ['Boyz', 'Gretchin', 'Nobz', 'Warboss', 'Weirdboy', 'Mekboy', 'Deffkopt']
CHAOS_MARINES_UNITS = ['Chaos Space Marines', 'Chaos Lord', 'Chaos Rhino', 'Chaos Land Raider', 'Chaos Bikers', 'Chaos Pilot', 'Chaos Priest']
ORC_LEADER = 'Chief Warmaster'
CHAOS_MARINES_LEADER = 'Corrupted Emperor'

class WarSimulator:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

    def generate_unit_names(self, race):
        prompt = (
            f"Generate 50 unique names for warriors belonging to {race} in the Warhammer 40k universe. "
            "List them with numbers from 1 to 50."
            "Name format: [first name] [last name]."
        )
        
        response = self.llm.invoke([("system", prompt)])
        names = response.content.strip().split("\n")
        return [name.split(". ", 1)[1].strip() for name in names if ". " in name]

    def assign_units(self, race):
        if race == 'Orc':
            units = ORC_UNITS
            leader = ORC_LEADER
        elif race == 'CHAOS MARINES':
            units = CHAOS_MARINES_UNITS
            leader = CHAOS_MARINES_LEADER
        else:
            raise ValueError("Invalid race. Choose 'Orc' or 'CHAOS MARINES'.")

        names = self.generate_unit_names(race)
        
        # Limit to 50 names if more are generated
        if len(names) > 50:
            names = names[:50]

        assigned_units = []
        for name in names:
            unit = random.choice(units)
            assigned_units.append({'name': name, 'unit': unit})

        # Randomly assign one leader
        leader_index = random.randint(0, len(assigned_units) - 1)
        assigned_units[leader_index]['unit'] = leader

        return assigned_units
    
    def generate_person_history(self, name, race):
        prompt = (
            f"Generate a lifestory for a warrior named {name} of the {race} in the Warhammer 40k universe. "
            "Include details about their background, training, and notable battles."
            "Write maximum 200 words."
        )
        
        response = self.llm.invoke([("system", prompt)])
        return response.content.strip()

    def generate_faction_data(self, race):
        if race not in RACE_LIST:
            raise ValueError(f"Invalid race. Available races: {RACE_LIST}")
        
        faction_data = self.assign_units(race)
        for unit in faction_data:
            unit['history'] = self.generate_person_history(unit['name'], race)
        df = pl.DataFrame(faction_data)  # Use polars DataFrame
        # rename columns to FIGHTER_NAME, CLASS, ORIGIN_HISTORY
        df = df.rename({'name': 'FIGHTER_NAME', 'unit': 'CLASS', 'history': 'ORIGIN_HISTORY'})
        return df

# Example usage
if __name__ == "__main__":
    war_simulator = WarSimulator(OPENAI_API_KEY)
    orc_data = war_simulator.generate_faction_data('Orc')
    # struct orc data as a DataFrame with columns 