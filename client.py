import logging
from typing import Any
import sys

import httpx
from pydantic import BaseModel

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

url = "https://test.fair.labdb.eu.org"


class User(BaseModel):
    userid: int
    firstname: str
    lastname: str
    email: str


def get_equipment_templates(equipment_name: str):
    response = httpx.get(f"{url}/equipment/{equipment_name}", verify=False)

    if response.status_code == 200:
        data = response.json()
        logger.info("Request successful!")
        return data
    else:
        logger.error(
            f"No equipment was found with name: {equipment_name}", response.status_code
        )
        raise Exception


def get_all_users() -> list[User]:
    response = httpx.get(f"{url}/users", verify=False)
    return response.json()


def get_users_teams(user_id: int) -> list[User]:
    response = httpx.get(f"{url}/users/{user_id}", verify=False)
    return response.json()


def create_new_experiment(experiment_template: dict[str, Any]):
    response = httpx.post(
        f"{url}/experiments",
        json=experiment_template,
        verify=False
    )

    if response.status_code == 200:
        logger.info("Experiment successfully Created!")


experiment = {
    "title": "test_test",
    "category_id": 113,
    "metadata": {"elabftw": {"extra_fields_groups": [{"id": 1, "name": "measurement_parameters"}]}, "extra_fields": {
        "start_frequency": {"type": "number", "unit": "Hz", "units": ["Hz"], "value": "", "group_id": 1}}},
    "userid": 21,
    "team_name": "SiGe"
}

if __name__ == "__main__":
    templates_list = get_equipment_templates("radio_frequency_station")
    users_list = get_all_users()
    user_teams = get_users_teams(user_id=22)
    experiment = {
        "title": "test_test",
        "category_id": templates_list["field_magnetic_resonance"]["id"],
        "metadata": templates_list["field_magnetic_resonance"]["metadata"],
        "userid": 22,
        "team_name": user_teams[0]["name"]
    } 
    create_new_experiment(experiment_template=experiment)