from uvicore import log
from faker import Faker
from uvicore.auth.models.user import User
from uvicore.support.dumper import dump, dd

def seed():
    log.item('Seeding table users')
    users = []
    fake = Faker()
    for _ in range(2):
        user = User(
            email=fake.email()
        )
        user.save()
        #posts.append(post)

    #dump(posts)
