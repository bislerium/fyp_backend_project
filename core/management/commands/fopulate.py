from faker import Faker
from faker.providers import internet, geo

fake = Faker()
fake.add_provider(internet)
