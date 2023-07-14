import contextvars
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import psycopg2
from dotenv import load_dotenv
import openai
from openai import ChatCompletion
from typing import Optional, Dict

app = FastAPI()
templates = Jinja2Templates(directory="templates")
load_dotenv()

#openai_model = "text-davinci-003"
openai_model = "gpt-3.5-turbo-16k-0613"
#openai_model = "gpt-3.5-turbo-16k"
openai.api_key = os.getenv("OPENAI_API_KEY")

db_name = os.getenv("DB_NAME")  
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")  
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")


conn = psycopg2.connect(
    dbname=db_name, 
    user=db_user, 
    password=db_pass, 
    host=db_host, 
    port=db_port,
    options="-c search_path=public"
)


conn
app.state.db_info: Dict[str, Dict[str, Dict]] = {}


app.state.table_result = []

app.state.natural_language_query = ''
app.state.sql_query = ''
app.state.output = ''


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    cursor = conn.cursor()  
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' and table_name in ('environments','documents','audit_summary2','ADS_EVENT_TYPE_STR');")
    table_names = [row[0] for row in cursor.fetchall()]
    #app.state.table_result = table_names
    
    app.state.db_info[db_name] = {}
    #table_names = 'documents'
    for table in table_names:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
        app.state.db_info[db_name][table] = {row[0]: row[1] for row in cursor.fetchall()}
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/nlp-text/")
async def fetch_table_names(request: Request):
    form_data = await request.form()
    input_data = form_data.get("input_data")
    app.state.button_value = form_data.get("button")
    app.state.natural_language_query = input_data
    
    
    return RedirectResponse(url="/query/", status_code=303)

@app.get("/query/")
async def get_query(request : Request):
   
    if app.state.natural_language_query is None:
        return {"error": "No query provided"}

    database_info = app.state.db_info[db_name]
    
    database_prompt = f"db name: '{db_name}', data structure: {database_info},db name: 'public'"

    # max_prompt_length = 300  
    # if len(app.state.natural_language_query) > max_prompt_length:
    #     app.state.natural_language_query = app.state.natural_language_query[:max_prompt_length]

    
    prompt = f"Promted:\n{app.state.natural_language_query}\n{database_prompt}\nSQL:"

    try:
        response = openai.ChatCompletion.create(
            model=openai_model,
            #prompt=prompt,
            messages=[{"role": "system", "content": prompt},],
            temperature=0.3,
            max_tokens=600
        )
    except Exception as e:
        return {"error": f"Error during query generation: {e}"}

   # app.state.sql_query = response['choices'][0]['message']['content'] 
    #app.state.sql_query = response
    app.state.sql_query = response['choices'][0]['message']['content']
    app.state.sql_query = app.state.sql_query.replace(f"{db_name}.", "")
    
    if app.state.button_value == 'button1':
        return RedirectResponse(url="/result/", status_code=303)
    else:
        return RedirectResponse(url="/db-execute/", status_code=303)
        
    
@app.get("/db-execute/")
async def get_query(request : Request):
    try:
        cursor = conn.cursor()
        cursor.execute(app.state.sql_query)
        if app.state.sql_query.lower().startswith("select"):  # si es una instrucción SELECT
            app.state.output = cursor.fetchall()
            return RedirectResponse(url="/result/", status_code=303)
            #print(f"Query results: {rows}")  # imprime los resultados
            #return {"Query results": rows}  # retorna la consulta con los resultados
        conn.commit()  # hacer commit
    except Exception as e:
        conn.rollback()  # rollback en caso de error
        return {"error": f"Error during database query: {e}"}

    return {"message": "Query executed successfully"}

  
  

@app.get("/result/", response_class=HTMLResponse)
async def show_result(request: Request):
    if app.state.output == '':
        result = app.state.sql_query
    else:
        result = app.state.output
    
    return templates.TemplateResponse("table.html", {"request": request, "result": result})
