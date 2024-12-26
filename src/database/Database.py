from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine,Session, select
from src.database.Model import Thought

class Database:
	def __init__(self) -> None:
		self.engine:Engine = create_engine("sqlite:///data//thoughts.db")
		SQLModel.metadata.create_all(self.engine)

	def addThought(self,title,description,html,css=None,public=False) -> None:
		newThought = Thought(
				title=title,
				description=description,
				htmlContent=html,
				cssContent=css,
				public=public)
		with Session(self.engine) as session:
			session.add(instance=newThought)
			session.commit()

	def deleteThought(self,thoughtId) -> None:
		thought:Thought | None = self._getThoughtById(thoughtId)
		with Session(self.engine) as session:
			session.delete(thought)
			session.commit()

	def editThought(self,thoughtId,title=None,description=None,html=None,css=None) -> None:
		with Session(self.engine) as session:
			thought:Thought | None = self._getThoughtById(thoughtId)
			session.delete(thought)
			thought.title = title if title is not None else thought.title
			thought.description = description if description is not None else thought.description
			thought.htmlContent = html if html is not None else thought.htmlContent
			thought.cssContent = css if css is not None else thought.cssContent
			session.add(thought)
			session.commit()

	def publishThought(self,thoughtId) -> None:
		with Session(self.engine) as session:
			thought:Thought | None = self._getThoughtById(thoughtId)
			session.delete(thought)
			thought.public = True
			session.add(thought)
			session.commit()

	def privateThought(self,thoughtId) -> None:
		with Session(self.engine) as session:
			thought = self._getThoughtById(thoughtId)
			session.delete(thought)
			thought.public = False
			session.add(thought)
			session.commit()

	def getAllThoughts(self,includeUnpublished=False):
		with Session(self.engine) as session:
			if includeUnpublished:
				thoughts = session.exec(select(Thought)).all()
			else:
				thoughts = session.exec(select(Thought).where(Thought.public)).all()
		return thoughts

	def getThoughtIdByTitle(self,title):
		with Session(self.engine) as session:
			thought = session.exec(select(Thought).where(Thought.title == title)).first()
			print(thought)
		return thought.thoughtId

	def getThoughtContent(self,thoughtId):
		thought = self._getThoughtById(thoughtId)
		return [thought.title,thought.description,thought.htmlContent,thought.cssContent,thought.createdAt,thought.updatedAt]

	def _getThoughtById(self,thoughtId):
		with Session(self.engine) as session:
			thought = session.exec(select(Thought).where(Thought.thoughtId == thoughtId)).first()
		return thought