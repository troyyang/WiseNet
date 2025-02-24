from sqlalchemy import BigInteger, Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from . import BaseModel

class User(BaseModel):
    __allow_unmapped__ = True
    __tablename__ = "users"

    username = Column(String(150), unique=True, index=True)
    email = Column(String(150), unique=True, index=True)
    mobile = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    role = Column(String(20), nullable=False, default='USER')

    def __repr__(self):
        repr = super().__repr__()
        return f"User({repr}, username={self.username}, email={self.email}, mobile={self.mobile}, role={self.role})"

class KnowledgeLib(BaseModel):
    __allow_unmapped__ = True
    __tablename__ = 'knowledge_lib'

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='PENDING')
    
    def __repr__(self):
        repr = super().__repr__()
        return f"KnowledgeLib({repr}, title={self.title}, content={self.content})"

class KnowledgeLibSubject(BaseModel):
    __allow_unmapped__ = True
    __tablename__ = 'knowledge_lib_subject'

    name = Column(String(200), nullable=False)
    knowledge_lib_id = Column(BigInteger, ForeignKey('knowledge_lib.id'))
    knowledge_lib = relationship('KnowledgeLib', backref='subjects')

    def __repr__(self):
        repr = super().__repr__()
        return f"KnowledgeLibSubject({repr}, name={self.name})"