import os
import bcrypt
from neomodel import config, DoesNotExist
from core.models import User
from dotenv import load_dotenv

load_dotenv()

# Configure neomodel to connect to your database
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEOMODEL_NEO4J_BOLT_URL = f"bolt://neo4j:{NEO4J_PASSWORD}@db:7687"
config.DATABASE_URL = NEOMODEL_NEO4J_BOLT_URL


print("========================")
print(f"{NEO4J_PASSWORD=}")
print(f"{NEOMODEL_NEO4J_BOLT_URL=}")
print("========================")


def create_admin_user(email, password, name):
    try:
        User.nodes.get(email=email)
        print(f"Admin user with email '{email}' already exists.")
        return
    except DoesNotExist:
        print("Creating a new admin user...")
        # Hash the password
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create the user node
        admin_user = User(
            email=email, name=name, password=hashed_password, role="ADMIN"
        )
        admin_user.save()
        print(f"Admin user '{name}' created successfully.")


if __name__ == "__main__":
    import getpass

    print("Welcome to the grocery system admin creator.")
    # email = input("Enter admin email: ")
    email = "hussain@gmail.com"
    # name = input("Enter admin name: ")
    name = "hussain"
    # password = getpass.getpass("Enter password: ")
    password = "password"
    create_admin_user(email, password, name)
