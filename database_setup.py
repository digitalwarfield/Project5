from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        String,
                        Text,
                        Index,
                        DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
import json

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    email = Column(String(256),
                   nullable=False,
                   unique=True)
    user_id = Column(Integer, primary_key=True)
    picture = Column(Text)
    full_name = Column(String(256))


class Categories(Base):
    __tablename__ = 'categories'
    # Only allow for one category to be added regardless of case
    name = Column(String(100), nullable=False, unique=True)
    cat_id = Column(Integer, primary_key=True)
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.cat_id,
        }


class Items(Base):
    __tablename__ = 'items'
    title = Column(String(80), nullable=False)
    item_id = Column(Integer, primary_key=True)
    description = Column(Text)
    last_update = Column(DateTime(timezone=True),
                         default=datetime.now(),
                         onupdate=datetime.now())
    cat_id = Column(Integer, ForeignKey('categories.cat_id'))
    categories = relationship(Categories)
    users = relationship(Users)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'title': self.title,
            'description': self.description,
            'item_id': self.item_id,
            'cat_id': self.cat_id
        }


# This is used to only allow one title per category
Index('uniqueTitlePerCategory', Items.title, Items.cat_id, unique=True)


try:
    database_login_file = open("/var/www/html/app_config.json", "r")
    database_login = json.load(database_login_file)
    user = database_login["db_user"]
    password = database_login["db_pass"]
    database = database_login["db_database"]
except Exception:
    print("Failed to open database login file")
    raise


database_params = "postgresql://{}:{}@localhost/{}".format(user,
                                                           password,
                                                           database)
engine = create_engine(database_params)


Base.metadata.create_all(engine)
