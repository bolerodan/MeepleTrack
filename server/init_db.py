from meeple.user import User
from meeple.roles import Role
from meeple import user_datastore,db
from meeple.properties import PropertyDef



db.create_all()
user_datastore.create_role(name="Admin",description="This is the admin role!!!")
user_datastore.create_role(name="User",description="Standard user role")
user = user_datastore.create_user(email='dan@dan.com', password='password',firstname="Dan",lastname="Wallace")
db.session.commit()

admin_role = Role.query.filter_by(name="Admin").first()
user_datastore.add_role_to_user(user,admin_role)




DEFAULT_PROP_NAMES = [("color","string"),("points","string")]

for n,t in DEFAULT_PROP_NAMES:
	query_prop = PropertyDef.query.filter(PropertyDef.name == n).first()
	if query_prop is None:
		new_prop = PropertyDef()
		new_prop.name = n
		new_prop.type = t
		meeple.db.session.add(new_prop)


db.session.commit()