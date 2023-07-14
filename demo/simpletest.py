from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI,Request, Header
from openai import Completion
from typing import Optional, Dict
import uvicorn


app = FastAPI()
templates = Jinja2Templates(directory="templates")
load_dotenv()

#openai.api_key = os.getenv("OPENAI_API_KEY")
#openai_model = "text-davinci-002"  
db_name = os.getenv("DB_NAME")  
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")  
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

print(db_name,db_user,db_pass,db_host,db_port)

conn = psycopg2.connect(
    dbname='metaminer', 
    user=db_user, 
    password=db_pass, 
    host=db_host, 
    port=db_port
)

cursor = conn.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
table_names = [row[0] for row in cursor.fetchall()]
result = table_names
print((result[0]))
for table in result:
    print(table)
conn.set_session(database = 'myspace')
print(conn)


conn = psycopg2.connect(
    dbname=db_name, 
    user=db_user, 
    password=db_pass, 
    host=db_host, 
    port=db_port
)

conn
db_info: Dict[str, Dict[str, Dict]] = {}
type(db_info)