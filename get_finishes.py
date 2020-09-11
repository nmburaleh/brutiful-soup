import requests
import pandas as pd

from IPython.display import display, HTML
from bs4 import BeautifulSoup
from bs4.element import ResultSet

BASE_URL = "http://ufcstats.com/fighter-details/"
COLUMNS = ["Combatants", "Event"]

filtering_logic = {
    0: lambda x: None,
    1: lambda x: tuple(x.get_text().strip().replace("\n", "").split("                      ")), # combatants
    2: lambda x: None, 3: lambda x: None,
    4: lambda x: None, 5: lambda x: None,
    6: lambda x: x.get_text().strip().replace("\n", "").replace("                              ", " "), # event
    7: lambda x: None,
    8: lambda x: x.get_text().strip(),                                   # round
    9: lambda x: x.get_text().strip()                                    # time
}

def is_valid_ufc_id(ufc_id: str) -> bool:
    """
    Quick check to see if input string has characteristics of all fighter ids
    from the site http://ufcstats.com/
    """
    return (
        len(ufc_id) == 16 and ufc_id.isalnum()
    )


def scrape_page(ufc_id: str) -> ResultSet:
    """
    1) Make a request to http://ufcstats.com/
    2) Convert the response to a soup object.
    3) Extract the table rows and return to another function for further processing.
    """
    response = requests.get(BASE_URL + ufc_id)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table_rows = soup.find_all('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'})
    return table_rows
    

def is_finish(lst: list) -> bool:
    """
    To be used with the filter function, keep only the bouts that
    did NOT go the distance in a 3 or 5 round bout.
    NB: This will also get rid of doctor stoppages between rounds.
    """
    if (
        (lst[2] == "3" and lst[3] == "5:00") or
        (lst[2] == "5" and lst[3] == "5:00")
        ):
        return False
    return True


def convert_to_dataframe(table_rows: ResultSet) -> pd.DataFrame:
    """
    Apply a series of filtering logic, convert to pd.DataFrame and return.
    """
    data = [
        [filtering_logic[i](table_data) for i, table_data in enumerate(table_row.find_all('td')) if filtering_logic[i](table_data)]
        for table_row in table_rows
    ]
    
    # filter for the bouts that did not go the distance
    data_no_distance = [*filter(is_finish, data)]
    
    # get only the first two values of each list
    data_final = [*map(lambda x: [x[0], x[1]], data_no_distance)]
    
    df = pd.DataFrame.from_records(data_final, columns = COLUMNS)
    return df

        
def get_fight_finishes(ufc_id: str) -> pd.DataFrame:
    df = convert_to_dataframe(
            scrape_page(
                ufc_id
            )
        )
    return df
    

if __name__ == "__main__":
    flag = True
    while flag:
        user_ufc_id = input(f"Enter a valid fighter id from http://ufcstats.com/: ")
        if not is_valid_ufc_id(user_ufc_id):
            print("Invalid input...try again!")
            continue
        flag = False
        
    display(
        HTML(
            get_fight_finishes(user_ufc_id).to_html()
        )
    )