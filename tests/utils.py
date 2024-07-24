from faker import Faker
from uuid import uuid4
from passlib.pwd import genword


class FakeEntitiesFactory:
    def __init__(self):
        self.fake = Faker()

    def generate_base_user(self) -> dict:
        user = dict()
        user["id"] = uuid4()
        user["name"] = self.fake.first_name()
        user["surname"] = self.fake.last_name()
        user["username"] = self.fake.user_name()[:14]
        user["email"] = self.fake.email()
        user["role_id"] = 1
        user["password"] = genword(entropy=56) + "1"
        return user

    def generate_verified_user(self) -> dict:
        user = self.generate_base_user()
        user["is_verified"] = True
        return user

    def generate_admin_user(self) -> dict:
        user = self.generate_verified_user()
        user["role_id"] = 2
        return user

    def generate_blocked_user(self) -> dict:
        user = self.generate_verified_user()
        user["is_blocked"] = self.fake.boolean()
        return user


fake_factory = FakeEntitiesFactory()

print(fake_factory.generate_base_user())
