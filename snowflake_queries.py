get_all_orcs = """
SELECT * FROM CORE_FIGHTERS
WHERE CORE_FIGHTERS.race_id = %s;
;
"""


get_race_id = """   
SELECT RACE_ID FROM CORE_RACE 
WHERE RACE_NAME = %s;
"""

