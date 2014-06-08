import meeple

from meeple.properties import PropertyDef

DEFAULT_PROP_NAMES = [("color","string"),("points","string")]

for n,t in DEFAULT_PROP_NAMES:
	query_prop = PropertyDef.query.filter(PropertyDef.name == n).first()
	if query_prop is None:
		new_prop = PropertyDef()
		new_prop.name = n
		new_prop.type = t
		meeple.db.session.add(new_prop)
meeple.db.session.commit()
