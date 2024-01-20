from random import choice, randint
from faker import Faker
from requests import Response, post


def generate_data(count: int = 5) ->  list[dict[str, str | int | float]]:
    """Generate sample data."""
    fake = Faker()
    cabin_letters: list[str] = ['A','B','C','D','E','F','G']

    sample_data: list[dict[str, str | int]] = [
        {
            'PassengerId': str(randint(1,10)),
            'PassengerClass': choice(['First', 'Second', 'Third']),
            'Name': fake.name(),
            'Sex': choice(['Male', 'Female']),
            'Ticket': 'A/5 21171',
            'Age': randint(1,80),
            'SiblingSpouse': choice([1, 0, 3, 4, 2, 5, 8]),
            'ParentChild': choice([0, 1, 2, 5, 3, 4, 6]),
            'Fare': randint(0,500),
            'Cabin': f'{choice(cabin_letters)}{randint(1,101)}',
            'Embarked': choice(['S', 'C', 'Q'])
        }
        for _ in range(count)
    ]
    return {'Passengers': sample_data}


def post_data(data: list[dict[str, str | int | float]], url: str):
    resp: Response = post(url=url, json=data)
    if resp.ok:
        print(resp.json())
    else:
        print(resp.text)