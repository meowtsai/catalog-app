from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, Product, User

engine = create_engine('sqlite:///categoryproduct.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Jimmy Lo", email="jimmy@meowroll.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for Action
category1 = Category(name="Action")

session.add(category1)
session.commit()

product1 = Product(user_id=1, name="Titanfall 2", description="Titanfall 2 is a first-person shooter from Respawn Entertainment that will be a multi-platform title.",
                   category=category1)

session.add(product1)
session.commit()


product2 = Product(user_id=1, name="Sonic Mania", description="Sonic Mania brings fans back into the 2D world of platform games with nostalgic pixel-style art and core classic gameplay by reimagining iconic Zones and Acts from Sonic The Hedgehog.",
                   category=category1)

session.add(product2)
session.commit()

# Menu for MMOs
category2 = Category(name="MMOs")

session.add(category2)
session.commit()

product1 = Product(user_id=1, name="Final Fantasy 14Stormblood", description="The second expansion for Final Fantasy 14, and the games best content yet.",
                   category=category2)

session.add(product1)
session.commit()


product2 = Product(user_id=1, name="Secret World Legends", description="The free to play relaunch of The Secret World, one of the most interesting MMOs of the past few years. The urban fantasy setting is unusual for an MMO, as is its focus on quality writing and smart quests. The Secret World was never a huge hit, and Legends doesn't massively overhaul it, but it's a cool alternative to more traditional MMOs like WoW and Final Fantasy 14. We gave it a 76 in our review, writing a less dramatic reimagining than it pretends to be, but hopefully enough to breathe new life into the coolest MMO universe around.",
                   category=category2)

session.add(product2)
session.commit()



# Menu for RPGs
category3 = Category(name="RPGs")

session.add(category3)
session.commit()

product1 = Product(user_id=1, name="Mount & Blade 2: Bannerlord", description="Part spectacle, part sim, part sandbox RPG, Mount & Blade remains a one-of-a-kind blend of systems and ideas. It's the thrill of being in a battle that's way bigger than you, of launching a single arrow into a horde of 50 dudes storming your castle. And it's the fun of being an average lord in a churning political and military sea of medieval NPCs.",
                   category=category3)

session.add(product1)
session.commit()


product2 = Product(user_id=1, name="Vampyr", description="As a doctor stricken with vampirism, youll face the challenge of trying to honor the Hippocratic Oath while also devouring people for their blood.",
                   category=category3)

session.add(product2)
session.commit()



print "added dummy data"
