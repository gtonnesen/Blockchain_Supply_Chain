from app import app, db
from ..models import User
from ..services.user_services import generate_user_keys


@app.cli.command()
def seed_database():
    print('Seeding...')

    # Seeding the User Table
    companies = [{'name': 'Walmart', 'role': 'Retailer'},
                 {'name': 'Top Line', 'role': 'Supplier'},
                 {'name': 'Canada Post', 'role': 'Courier'}]
    password = 'Password123!'
    if db.session.query(User).scalar() is None:
        print('Seeding User table...')
        users = []
        for company in companies:
            name = company['name'].replace(' ', '').lower()
            user = User(username=name, email='{}@mail.com'.format(name), company=company['name'],
                        user_role=company['role'])
            user.private_key, user.public_key = generate_user_keys()
            user.set_password(password)
            db.session.add(user)
        # db.session.add(users)
        db.session.commit()

    print('Done.')
