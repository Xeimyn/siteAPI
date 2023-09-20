from datetime import datetime
import hashlib
import sqlite3
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

dev = FastAPI(docs_url="/dev",title="JCMS.DEV Blog API")

pw_hash = "d69457b93bc60b8b5e7dd7e8dc6bff6d"

class addThoughtRequest(BaseModel): 
	pw             : str # Authentication
	thoughtTitle   : str # Thought Title
	thoughtContent : str # Thought Text
	thoughtCSS     : str # CSS File to generate
	published      : int # if it should be returned for /getContent currently

class editThoughtRequest(BaseModel): 
	pw             : str # Authentication
	thoughtID      : int # Thought Title
	thoughtTitle   : str # Thought Title
	thoughtContent : str # Thought Text
	thoughtCSS     : str # CSS File to generate
	published      : int # if it should be returned for /getContent currently

class getContent(BaseModel):
	pw             : str # Authentication
	thoughtTitle   : str 

class authenticated(BaseModel):
	pw             : str # Authentication

class viewRequest(BaseModel):
	thoughtID      : int

@dev.post("/addView")
async def addView(request_data: viewRequest):
	t_id = int(request_data.thoughtID)
	db,c = getDBandC()
	c.execute("SELECT views FROM Thoughts WHERE thoughtID = ?", (t_id,))	
	currentViews = c.fetchone()
	if currentViews is None:
		db.close()
		return {"message" : f"Thought with id {t_id} not found."}
	currentViews = currentViews[0]
	c.execute("UPDATE Thoughts SET views = ? WHERE thoughtID = ?",(int(currentViews) + 1,t_id,))
	db.commit()
	db.close()
	return {"message", "You aren't botting my blog with views like a weirdo right?"}

@dev.get("/getTitlesAndDates")
async def getTitles(request_data: authenticated) -> dict[str, str]:
	"returns titles and dates. returns unpublished ones if password is provided"
	pw = None if getHashedPw(request_data.pw) != pw_hash else "authenticated"
	db,c = getDBandC()
	if pw is None:
		c.execute("SELECT thoughtTitle,creationDate from Thoughts WHERE published = ?", (isPublished.yes,))
	else:
		c.execute("SELECT thoughtTitle,creationDate from Thoughts")
	titles = str([title for title in c.fetchall()])
	db.close()
	return {"message" : titles}

@dev.get("/getContent")
async def getContent(request_data: getContent) -> dict[str, str]:
	thoughtTitle = request_data.thoughtTitle
	pw = None if getHashedPw(request_data.pw) != pw_hash else "authenticated"
	db,c = getDBandC()
	if pw is None:
		c.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID from Thoughts WHERE thoughtTitle = ? and published = ?", (thoughtTitle,isPublished.yes,))
	else:
		c.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID from Thoughts WHERE thoughtTitle = ?", (thoughtTitle,))
	rawData = c.fetchone()
	if rawData is None:
		db.close()
		return {"message" : f"Thought with title {thoughtTitle} not found"}
	niceData = { "message": str({
		"thoughtTitle": rawData[0],	
		"thoughtContent": rawData[1],	
		"thoughtCSS": rawData[2],	
		"creationDate": rawData[3],	
		"thoughtID": rawData[4],	
		})
	}
	db.close()
	return niceData

@dev.post("/addThought")
async def addThought(request_data: addThoughtRequest):
	pw = None if getHashedPw(request_data.pw) != pw_hash else "authenticated"
	if pw is None:
		return {"message" : "Stwop twying pwease. (^3^)"}
	thoughtTitle   = str(request_data.thoughtTitle)
	thoughtContent = str(request_data.thoughtContent)
	thoughtCSS     = str(request_data.thoughtCSS)
	creationDate   = int(getTimestamp())
	published      = int(request_data.published)
	db,c = getDBandC()
	# If there are no ids where the title is the same as the submitted title
	if existingThoughtId := c.execute("SELECT thoughtID from Thoughts WHERE thoughtTitle = ?",(thoughtTitle,)).fetchone() is None:
		c.execute("INSERT INTO Thoughts (thoughtTitle, thoughtContent, thoughtCSS, creationDate, published) VALUES (?,?,?,?,?)", (thoughtTitle, thoughtContent, thoughtCSS, creationDate, published,))
		db.commit()
		db.close
		return {"message" : f"Added Thought '{thoughtTitle}'"}
	else:
		db.close
		return {"message" : f"A thought with title {thoughtTitle} already exists."}

@dev.post("/editThought")
async def editThought(request_data: editThoughtRequest):
	pw = None if getHashedPw(request_data.pw) != pw_hash else "authenticated"
	if pw is None:
		return {"message" : "Stwop twying pwease. (^3^)"}
	thoughtID      = int(request_data.thoughtID)
	thoughtTitle   = str(request_data.thoughtTitle)
	thoughtContent = str(request_data.thoughtContent)
	thoughtCSS     = str(request_data.thoughtCSS)
	published      = int(request_data.published)
	db,c = getDBandC()
	c.execute("UPDATE Thoughts SET thoughtTitle = ?, thoughtContent = ?, thoughtCSS = ?, published = ? WHERE thoughtID = ?",(thoughtTitle, thoughtContent, thoughtCSS, published,thoughtID))
	db.commit()
	db.close()
	return {"message" : f"Updated Thought {thoughtTitle} ({thoughtID})"}

# ---

@dev.get("/{path}") 
async def deadLink(path: str):
	raise HTTPException(status_code=404, detail="Hippity Hoppity get off my Endpointitiy... yeah thats was bad im sorry")

# ---

def getHashedPw(pw) -> str:
	return hashlib.md5(str(pw).encode("utf-8")).hexdigest() 

def setupDB() -> None:
	db,c = getDBandC()
	c.execute("""CREATE TABLE IF NOT EXISTS Thoughts (
		   	thoughtID INTEGER PRIMARY KEY AUTOINCREMENT,
			thoughtTitle TEXT,
			thoughtContent TEXT,
			thoughtCSS TEXT,
			creationDate INTEGER DEFAULT 0,
			published INTEGER DEFAULT 0,
		   	views INTEGER DEFAULT 0
		)""")
	db.commit()
	db.close()
	exit()

def getDBandC():
	"returns a cursor and connection for the database"
	return [db := sqlite3.connect("db.db"),db.cursor()]

def getTimestamp() -> int:
	return int(datetime.now().timestamp())

class isPublished: 
	yes = 1
	no  = 0

if __name__ == "__main__":
	setupDB()