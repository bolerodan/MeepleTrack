import settings
import urllib2
import xml.etree.ElementTree as et
from game import Game
from sqlalchemy.exc import IntegrityError
from meeple_exceptions import GameNotFound

def getText(node,key):
    try:
        return node.find(key).text 
    except AttributeError:
        return None


#get builtin properties..duh
def get_builtin_properties(as_dict=False):
    from properties import PropertyDef
    return PropertyDef.query.filter(PropertyDef.creator_id == None).all()


def addplayer_helper(gs,new_player):
    import meeple
    from properties import PropertyDef,GameSessionProperties,Property
    builtin_props = get_builtin_properties()
    builtin_props_all = []#what to return to the browser when adding a user
    for propdef in builtin_props:
        default = Property()
        default.propdef = propdef
        meeple.db.session.add(default)        
        gsp = GameSessionProperties()
        gsp.gamesession = gs
        gsp.user = new_player
        gsp.property = default
        meeple.db.session.flush()
        builtin_props_all.append(gsp.as_dict())
        meeple.db.session.add(gsp)     
    return builtin_props_all   

#gameid comes from BGG api. Not internal
def build_game(gameid,expansions=False):
    url = "%s/boardgame/%s" % (settings.BGG_API,gameid)
    response = urllib2.urlopen(url)
    xml_string = response.read()

    bg_tree = et.fromstring(xml_string)

    if bg_tree.find('boardgame').find('error') is not None:
        """This happens if BGG cannot find the board game.. so get their error message"""
        raise GameNotFound(bg_tree.find('boardgame').find('error').attrib['message'])
    bg_xml = bg_tree.find('boardgame')
    game = Game()
    game.game_id = gameid
    game.name = getText(bg_xml,'name')
    game.thumbnail = getText(bg_xml,'thumbnail')
    game.image = getText(bg_xml,'image')
    game.minplayers = getText(bg_xml,'minplayers')
    game.yearpublished = getText(bg_xml,'yearpublished')
    game.maxplayers = getText(bg_xml,'maxplayers')
    game.playingtime = getText(bg_xml,'playingtime')
    game.description = getText(bg_xml,'description')
    for publisher in bg_xml.iter('boardgamepublisher'):
        game.addPublisher(publisher.text)
    for category in bg_xml.iter('boardgamecategory'):
        game.addCategory(category.text)
    for mechanic in bg_xml.iter('boardgamemechanic'):
        game.addMechanic(mechanic.text)
    if expansions:     
        import meeple
        meeple.db.session.flush() #this is needed for expansions. Incase we get duplicate IDs
        for expansion in bg_xml.iter('boardgameexpansion'):
            
            expansion_id = expansion.attrib.get('objectid')
            inbound = expansion.attrib.get('inbound')
            if inbound is None and inbound is not True:
                try:
                    expansion_game = Game.query.filter(Game.game_id == expansion_id).first()  
                    print expansion_game            
                    if expansion_game is None:              
                        expansion_game = build_game(expansion_id,True)
                        print "Expansion ID: ", expansion_game.game_id, " For ID:", gameid
                    game.expansions.append(expansion_game)
                except IntegrityError:
                    pass # :(!!!
    return game



def build_search(term):
    url = "%s/search?search=%s" % (settings.BGG_API,term)
    response = urllib2.urlopen(url)
    xml_string = response.read()

    results = []
    sr_tree = et.fromstring(xml_string) 
    for r in sr_tree:
        result = {}
        result['name'] = r.find('name').text
        result['id'] = r.attrib['objectid']
        result['thumbnail'] = getText(r,'thumbnail')
        results.append(result)
    return results
