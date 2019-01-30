import sys
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


Base = declarative_base()


class Categories(Base):
    __tablename__ = 'categories'
    # Only allow for one category to be added regardless of case
    name = Column(String(128, collation='NOCASE'), nullable=False, unique=True)
    cat_id = Column(Integer, primary_key=True)
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.cat_id,
        }


class Items(Base):
    __tablename__ = 'items'
    title = Column(String(80, collation='NOCASE'), nullable=False)
    item_id = Column(Integer, primary_key=True)
    description = Column(Text)
    last_update = Column(DateTime(timezone=True),
                         default=datetime.now(),
                         onupdate=datetime.now())
    cat_id = Column(Integer, ForeignKey('categories.cat_id'))
    categories = relationship(Categories)

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
engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
