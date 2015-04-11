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
    print "***REQUESTING REMOTE API CALL***"
    if isinstance(gameid,list):
        is_list = True
        print "LIST ",gameid
        gameid = ",".join(map(str, gameid))
    url = "%s/boardgame/%s" % (settings.BGG_API,gameid)
    response = urllib2.urlopen(url)
    xml_string = response.read()

    bg_tree = et.fromstring(xml_string)

    if bg_tree.find('boardgame').find('error') is not None:
        """This happens if BGG cannot find the board game.. so get their error message"""
        raise GameNotFound(bg_tree.find('boardgame').find('error').attrib['message'])
    bg_xml = bg_tree.find('boardgame')

    games = []
    for g in bg_tree.iter('boardgame'):
        try:
            game = Game()
            game.game_id = g.attrib.get('objectid')
            game.name = getText(g,'name')
            game.thumbnail = getText(g,'thumbnail')
            game.image = getText(g,'image')
            game.minplayers = getText(g,'minplayers')
            game.yearpublished = getText(g,'yearpublished')
            game.maxplayers = getText(g,'maxplayers')
            game.playingtime = getText(g,'playingtime')
            game.description = getText(g,'description')
            for publisher in g.iter('boardgamepublisher'):
                game.addPublisher(publisher.text)
            for category in g.iter('boardgamecategory'):
                game.addCategory(category.text)
            for mechanic in g.iter('boardgamemechanic'):
                game.addMechanic(mechanic.text)
            if expansions:     
                import meeple
                print "Get expansion for id ",game.game_id
                meeple.db.session.flush() #this is needed for expansions. Incase we get duplicate IDs
                for expansion in g.iter('boardgameexpansion'):
                    
                    expansion_id = expansion.attrib.get('objectid')
                    print "Expansion ID",expansion_id
                    inbound = expansion.attrib.get('inbound')
                    if inbound is None and inbound is not True:
                        try:
                            expansion_game = Game.query.filter(Game.game_id == expansion_id).first()  
                            if expansion_game is None:              
                                expansion_game = build_game(expansion_id,False)
                            game.expansions.append(expansion_game)
                        except IntegrityError:
                            pass # :(!!!
            games.append(game)
        except IntegrityError:
            pass

    if is_list:
        #if we are list of ids, return a list of games
        return games
    else:
        return games[0]


def get_expansions(game):
    url = "%s/boardgame/%s" % (settings.BGG_API,game.game_id)
    response = urllib2.urlopen(url)
    xml_string = response.read()

    bg_tree = et.fromstring(xml_string)

    if bg_tree.find('boardgame').find('error') is not None:
        """This happens if BGG cannot find the board game.. so get their error message"""
        raise GameNotFound(bg_tree.find('boardgame').find('error').attrib['message'])
    bg_xml = bg_tree.find('boardgame')
    expansions = []
    for expansion in bg_xml.iter('boardgameexpansion'):
        
        expansion_id = expansion.attrib.get('objectid')
        inbound = expansion.attrib.get('inbound')
        if inbound is None and inbound is not True:
            try:
                expansion_game = Game.query.filter(Game.game_id == expansion_id).first()  
                if expansion_game is None:              
                    expansion_game = build_game(expansion_id,False)
                    print "ex_game",expansion_game
                expansions.append(expansion_game)
            except IntegrityError:
                pass # :(!!!   

    return expansions



def build_search(term,id_only=False):
    url = "%s/search?search=%s" % (settings.BGG_API,term)
    response = urllib2.urlopen(url)
    xml_string = response.read()

    results = []
    sr_tree = et.fromstring(xml_string) 
    for r in sr_tree:
        if id_only:
            result = r.attrib['objectid']
        else:
            result = {}
            result['name'] = r.find('name').text
            result['id'] = r.attrib['objectid']
            result['thumbnail'] = getText(r,'thumbnail')
        results.append(result)
    return results
