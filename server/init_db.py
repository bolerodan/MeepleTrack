from meeple.user import User
from meeple.roles import Role
from meeple import user_datastore,db




db.create_all()
user_datastore.create_role(name="Admin",description="This is the admin role!!!")
user_datastore.create_role(name="User",description="Standard user role")
user = user_datastore.create_user(email='dan@dan.com', password='password',firstname="Dan",lastname="Wallace")
db.session.commit()

admin_role = Role.query.filter_by(name="Admin").first()
user_datastore.add_role_to_user(user,admin_role)

db.session.commit()