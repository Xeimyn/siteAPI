from sqlmodel import SQLModel, create_engine,Session, select
from src.database.Model import Thought

class Database:
	def __init__(self):
		self.engine = create_engine("sqlite:///data//thoughts.db")
		SQLModel.metadata.create_all(bind=self.engine)

	def addThought(self,title,description,html,css=None):
		newThought = Thought(
				title=title,
				description=description,
				htmlContent=html,
				cssContent=css)
		with Session(bind=self.engine) as session:
			session.add(instance=newThought)
			session.commit()

	def deleteThought(self,thoughtId):
		with Session(bind=self.engine) as session:
			thought = session.exec(select(Thought).where(Thought.thoughtId == thoughtId)).first()
			session.delete(thought)

	def editThought(self,thoughtId,title=None,description=None,html=None,css=None):
		toUpdate = [item for item in [title,description,html,css] if item != None]
		# If there is nothing to update return early
		if len(toUpdate) == 0:
			return False
		with Session(bind=self.engine) as session:
			thought = session.exec(select(Thought).where(Thought.thoughtId == thoughtId)).first()
			for item in toUpdate:
				thought.

	def publishThought(self,thoughtId):
		print(f"publishing thought with thoughtId {thoughtId}")
		return "status"

	def privateThought(self,thoughtId):
		print(f"privating thought with thoughtId {thoughtId}")
		return "status"

	def getAllThoughts(self,includeUnpublished=False):
		print("Getting all thoughts") if includeUnpublished else print("Getting all (public) thoughts")
		return [{"title":"title","description":"description","createdAt":"createdAt","updatedAt":"updatedAt"},]

	def getThoughthoughtIdByTitle(self,title):
		print("here is your id sir")
		return "thoughtId"

	def getThoughtContent(self,thoughtId):
		print("here is your content sir")
		return "title,description,html,css,created_at,updated_at"
