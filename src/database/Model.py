import time
from sqlmodel import SQLModel,Field
from sqlalchemy import Column, String, event

class Thought(SQLModel,table=True):
	thoughtId:int|None = Field(default=None,primary_key=True,nullable=True)
	title:str = Field(sa_column=Column("name", String, unique=True))
	description:str = Field()
	htmlContent:str = Field()
	cssContent:str|None = Field(nullable=True)
	views:int = Field(default=0)
	public:bool = Field(default=False, index=True)
	createdAt:int = Field(default_factory=time.time)
	updatedAt:int|None = Field(default=None,nullable=True)

@event.listens_for(target=Thought,identifier="before_update")
def updateTimestamp(mapper,conn,target:Thought) -> None:
	target.updatedAt = time.time()