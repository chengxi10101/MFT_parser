from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///result.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class MFT(Base):
    __tablename__ = 'mft'
    idx = Column(Integer, 
                 Sequence('article_aid_seq', start=1, increment=1),   
                 primary_key=True)
    file_name = Column(String)
    file_size = Column(String)

    s_created_time = Column(String)
    s_created_time = Column(String)
    s_modified_time = Column(String)
    s_mft_modified_time = Column(String)
    s_last_accessed_time = Column(String)
    f_created_time = Column(String)
    f_modified_time = Column(String)
    f_mft_modified_time = Column(String)
    f_last_accessed_time = Column(String)

    is_deleted = Column(String)
    #file_full_path = Column(String)


def init_db():
    Base.metadata.drop_all(engine) 
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()