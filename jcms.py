from datetime import datetime
import sqlite3
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import bcrypt

# uvicorn jcms:dev --host 0.0.0.0 --port 80 --reload --no-server-header --no-date-header 

dev = FastAPI(docs_url="/dev",title="JCMS.DEV Thoughts API",)

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

class addThoughtRequest(BaseModel): 
	pw             : str # Authentication
	thoughtTitle   : str # Thought Title
	thoughtContent : str # Thought Text
	thoughtCSS     : str # CSS File to generate
	published      : int # if it should be returned for /getThought currently (without valid auth)

class editThoughtRequest(BaseModel): 
	pw             : str # Authentication
	thoughtID      : int # Thought Title
	thoughtTitle   : str # Thought Title
	thoughtContent : str # Thought Text
	thoughtCSS     : str # CSS File to generate
	published      : int # if it should be returned for /getThought currently

class getThoughtRequest(BaseModel):
	pw             : str # Authentication
	thoughtTitle   : str 

class authenticated(BaseModel):
	pw             : str # Authentication

class viewRequest(BaseModel):
	thoughtID      : int

# ---

@dev.post("/auth")
async def auth(request_data: authenticated):
	return bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash)

@dev.get("/addView")
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

@dev.post("/getTitlesAndDates")
async def getTitles(request_data: authenticated):
	"returns titles and dates. returns unpublished ones if password is provided"
	db,c = getDBandC()
	if not bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash):
		c.execute("SELECT thoughtTitle,creationDate from Thoughts WHERE published = ?", (thoughtIs.public,))
	else:
		c.execute("SELECT thoughtTitle,creationDate from Thoughts")
	titles = str([thought for thought in c.fetchall()])
	db.close()
	return {"message" : titles}

@dev.post("/getThought")
async def getThoughtRequest(request_data: getThoughtRequest):
	thoughtTitle = request_data.thoughtTitle
	db,c = getDBandC()
	if not bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash):
		c.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID,views from Thoughts WHERE thoughtTitle = ? and published = ?", (thoughtTitle,thoughtIs.public,))
	else:
		c.execute("SELECT thoughtTitle,thoughtContent,thoughtCSS,creationDate,thoughtID,views from Thoughts WHERE thoughtTitle = ?", (thoughtTitle,))
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
		"views": rawData[5],
		})
	}
	db.close()
	return niceData

@dev.post("/addThought")
async def addThought(request_data: addThoughtRequest):
	if not bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash):
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
	if not bcrypt.checkpw(str(request_data.pw).encode("utf-8"),pw_hash):
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

@dev.get("/") 
async def emptyLink():
	raise HTTPException(status_code=404, detail="Hippity Hoppity get off my Endpointitiy... yeah thats was bad im sorry")

# ---

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

class thoughtIs: 
	public = 1
	private  = 0

if __name__ == "__main__":
	setupDB()
