from datetime import datetime
import sqlite3
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

# uvicorn jcms:dev --host 0.0.0.0 --port 80 --reload --no-server-header --no-date-header 

dev = FastAPI(docs_url="/dev",title="JCMS.DEV Thoughts API",version="2.0.1")

# Allow all origins in development. You might want to restrict this in production.
origins = ["*"]

dev.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pw_hash = b'$2b$12$MJzi3icY0zCsnU8KSOYIh.32fvNoiFXsIa5lHPiw8M3RHBPM.mK.G'

# ---
class authenticated(BaseModel):
	password             : str # Authentication

class add_update_ThoughtRequest(authenticated): 
	thoughtTitle   : str # Thought Title
	thoughtContent : str # Thought Text
	thoughtCSS     : str # CSS File to generate
	published      : int # if it should be returned for /getThought currently (without valid auth)

class getThoughtRequest(authenticated):
	thoughtTitle   : str 

class authenticatedID(authenticated):
	thoughtID      : int

class thoughtID(BaseModel):
	thoughtID      : int

# ---

@dev.post("/auth")
async def auth(request_data: authenticated):
	return bcrypt.checkpw(str(request_data.password).encode("utf-8"),pw_hash)

@dev.post("/addView")
async def addView(request_data: thoughtID):
	db,cursor = getDBandCursor()
	cursor.execute("SELECT views FROM Thoughts WHERE thoughtID = ?", (request_data.thoughtID,))	
	currentViews = cursor.fetchone()
	if currentViews is None:
		db.close()
		return {"message" : f"Thought with id {request_data.thoughtID} not found."}
	print(currentViews)
	cursor.execute("UPDATE Thoughts SET views = ? WHERE thoughtID = ?",(currentViews[0] + 1,request_data.thoughtID,))
	db.commit()
	db.close()
	return {"message":"You aren't botting my blog with views like a weirdo right?"}

@dev.post("/getTitlesAndDates")
async def getTitles(request_data: authenticated):
	"returns titles and dates. returns unpublished ones if password is provided"
	db,cursor = getDBandCursor()
	if bcrypt.checkpw(request_data.password.encode("utf-8"),pw_hash):
		cursor.execute("SELECT thoughtTitle,creationDate from Thoughts")
	else:
		cursor.execute("SELECT thoughtTitle,creationDate from Thoughts WHERE published = ?", (thoughtIs.public,))
	result = [{"title":title,"date":date} for title,date in cursor.fetchall()]
	db.close()
	return {"message" : result}

@dev.post("/getThought")
async def getThoughtRequest(request_data: getThoughtRequest):
	thoughtTitle = request_data.thoughtTitle
	db,cursor = getDBandCursor()
	if bcrypt.checkpw(request_data.password.encode("utf-8"),pw_hash):
		cursor.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID,views from Thoughts WHERE thoughtTitle = ?", (thoughtTitle.lower(),))
	else:
		cursor.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID,views from Thoughts WHERE thoughtTitle = ? and published = ?", (thoughtTitle.lower(),thoughtIs.public,))
	rawData = cursor.fetchone()
	if rawData is None:
		db.close()
		return {"message" : f"Thought with title {thoughtTitle} not found"}
	niceData = { "message": str({
		"thoughtTitle": rawData[0],	
		"thoughtContent": rawData[1],	
		"thoughtCSS": rawData[2],	
		"creationDate": rawData[3],	
		"thoughtID": rawData[4],
		"views": rawData[5],
		})
	}
	db.close()
	return niceData

@dev.post("/addThought")
async def addThought(request_data: add_update_ThoughtRequest):
	if not bcrypt.checkpw(str(request_data.password).encode("utf-8"),pw_hash):
		return {"message" : "Stwop twying pwease. (^3^)"}
	thoughtTitle   = str(request_data.thoughtTitle).lower()
	thoughtContent = str(request_data.thoughtContent)
	thoughtCSS     = str(request_data.thoughtCSS)
	creationDate   = int(getTimestamp())
	published      = int(request_data.published)
	db,cursor = getDBandCursor()
	# If there are no ids where the title is the same as the submitted title
	if existingThoughtId := cursor.execute("SELECT thoughtID from Thoughts WHERE thoughtTitle = ?",(thoughtTitle,)).fetchone() is None:
		cursor.execute("INSERT INTO Thoughts (thoughtTitle, thoughtContent, thoughtCSS, creationDate, published) VALUES (?,?,?,?,?)", (thoughtTitle.lower(), thoughtContent, thoughtCSS, creationDate, published,))
		db.commit()
		db.close
		return {"message" : f"Added Thought '{thoughtTitle.lower()}'"}
	else:
		db.close
		return {"message" : f"A thought with title {thoughtTitle.lower()} already exists."}

@dev.post("/updateThought")
async def updateThought(request_data: add_update_ThoughtRequest):
	if not bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash):
		return {"message" : "Stwop twying pwease. (^3^)"}
	thoughtID      = int(request_data.thoughtID)
	thoughtTitle   = str(request_data.thoughtTitle).lower()
	thoughtContent = str(request_data.thoughtContent)
	thoughtCSS     = str(request_data.thoughtCSS)
	published      = int(request_data.published)
	db,c = getDBandCursor()
	c.execute("UPDATE Thoughts SET thoughtTitle = ?, thoughtContent = ?, thoughtCSS = ?, published = ? WHERE thoughtID = ?",(thoughtTitle, thoughtContent, thoughtCSS, published,thoughtID))
	db.commit()
	db.close()
	return {"message" : f"Updated Thought {thoughtTitle} ({thoughtID})"}

@dev.post("/deleteThought")
async def deleteThought(request_data: authenticatedID):
	if not bcrypt.checkpw(request_data.password.encode("utf-8"),pw_hash):
		return {"message" : "Stwop twying pwease. (^3^)"}
	db,cursor = getDBandCursor()
	thoughtTitle = cursor.execute("SELECT thoughtTitle from Thoughts WHERE thoughtID = ?",(request_data.thoughtID,)).fetchone()
	if thoughtTitle is None:
		db.close()
		return {"message" : f"Thought with id {request_data.thoughtID} not found."}
	thoughtID = cursor.execute("SELECT thoughtID from Thoughts WHERE thoughtID = ?",(request_data.thoughtID,)).fetchone()[0]
	cursor.execute("DELETE FROM Thoughts WHERE thoughtID = ?",(request_data.thoughtID,))
	db.commit()
	db.close()
	return {"message" : f"Deleted Thought {thoughtTitle[0]} ({thoughtID})"}

# ---

@dev.get("/{path}", include_in_schema=False) 
async def deadLinkGet(path: str):
	raise HTTPException(status_code=404, detail="Oh d-deweaw, it seems wike you've stumbled upon the elusive 404 tewwitowy, where the endpoints awe as scawce as a needle in a digital haystack (>///<). Awas, the endpoint you seek is pwaying hide-and-seek, perhaps engaged in a spirited game of 'Where in the Wowwd Wide Web is Cawmen Sandiego?' (*≧ω≦). Fweaw not, intwepid adventuwew, fow in the vast expanse of cyberspace, not evewy UWW is destined to be discuvwed. So, take a moment to appweciate the sewendipity of this encountew, and wemembew, the jouwney is often mowe entewtaining than the destination (*´꒳`*). If you're feeling pawticulawwy adventuwous, you may twy anothew path in the wabwyinth of UWWs or consuwt the ancient scwowls known as API documentation. Happy questing, and may youw HTTP wequests be evew in youw favow! (*^▽^*)")

@dev.post("/{path}", include_in_schema=False) 
async def deadLinkPost(path: str):
	raise HTTPException(status_code=404, detail="Oh d-deweaw, it seems wike you've stumbled upon the elusive 404 tewwitowy, where the endpoints awe as scawce as a needle in a digital haystack (>///<). Awas, the endpoint you seek is pwaying hide-and-seek, perhaps engaged in a spirited game of 'Where in the Wowwd Wide Web is Cawmen Sandiego?' (*≧ω≦). Fweaw not, intwepid adventuwew, fow in the vast expanse of cyberspace, not evewy UWW is destined to be discuvwed. So, take a moment to appweciate the sewendipity of this encountew, and wemembew, the jouwney is often mowe entewtaining than the destination (*´꒳`*). If you're feeling pawticulawwy adventuwous, you may twy anothew path in the wabwyinth of UWWs or consuwt the ancient scwowls known as API documentation. Happy questing, and may youw HTTP wequests be evew in youw favow! (*^▽^*)")

@dev.get("/", include_in_schema=False) 
async def emptyLink():
	raise HTTPException(status_code=404, detail="Oh d-deweaw, it seems wike you've stumbled upon the elusive 404 tewwitowy, where the endpoints awe as scawce as a needle in a digital haystack (>///<). Awas, the endpoint you seek is pwaying hide-and-seek, perhaps engaged in a spirited game of 'Where in the Wowwd Wide Web is Cawmen Sandiego?' (*≧ω≦). Fweaw not, intwepid adventuwew, fow in the vast expanse of cyberspace, not evewy UWW is destined to be discuvwed. So, take a moment to appweciate the sewendipity of this encountew, and wemembew, the jouwney is often mowe entewtaining than the destination (*´꒳`*). If you're feeling pawticulawwy adventuwous, you may twy anothew path in the wabwyinth of UWWs or consuwt the ancient scwowls known as API documentation. Happy questing, and may youw HTTP wequests be evew in youw favow! (*^▽^*)")

# ---

def setupDB() -> None:
	db,c = getDBandCursor()
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

def getDBandCursor():
	"returns a cursor and connection for the database"
	return [db := sqlite3.connect("db.db"),db.cursor()]

def getTimestamp() -> int:
	return int(datetime.now().timestamp())

class thoughtIs: 
	public = 1
	private  = 0

if __name__ == "__main__":
	setupDB()
