from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine,Session, select
from src.database.Model import Thought

class Database:
	def __init__(self) -> None:
		self.engine:Engine = create_engine("sqlite:///data//thoughts.db")
		SQLModel.metadata.create_all(self.engine)

	def addThought(self,title,description,html,css=None) -> None:
		newThought = Thought(
				title=title,
				description=description,
				htmlContent=html,
				cssContent=css)
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
			thought.title = title if title is not None else thought.title
			thought.description = description if description is not None else thought.description
			thought.html = html if html is not None else thought.html
			thought.css = css if css is not None else thought.css
			# TODO | Not sure if i only have to commit the session after editing the thought
			session.commit()

	def publishThought(self,thoughtId) -> None:
		with Session(self.engine) as session:
			thought:Thought | None = self._getThoughtById(thoughtId)
			thought.public = True
			session.commit()

	def privateThought(self,thoughtId) -> None:
		with Session(self.engine) as session:
			thought = self._getThoughtById(thoughtId)
			thought.public = False
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
			thoughtId = session.exec(select(Thought).where(Thought.title == title)).first().thoughtId
		return thoughtId

	def getThoughtContent(self,thoughtId):
		thought = self._getThoughtById(thoughtId)
		return [thought.title,thought.description,thought.html,thought.css,thought.createdAt,thought.updatedAt]

	def _getThoughtById(self,thoughtId):
		with Session(self.engine) as session:
			thought = session.exec(select(Thought).where(Thought.thoughtId == thoughtId)).first()
		return thought