from typing import Annotated
from src.database.Database import Database
from fastapi import FastAPI,Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib

app = FastAPI()
security = HTTPBasic()
db = Database()

@app.get("/thoughts")
def getAllThought():
	return db.getAllThoughts()

@app.get("/thought/{thoughtTitle}")
def getThoughtContent(thoughtTitle):
	tId = db.getThoughtIdByTitle(thoughtTitle)
	return db.getThoughtContent(tId)

# TODO | Authenticated endpoints
@app.get("/all")
def returnSecret(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
	if credentials.username == "Simon":
		return "ur allowed"
	else:
		return "ur not allowed"