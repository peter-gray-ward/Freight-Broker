import asyncpg
import os
import json

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "env.json"))
schemas_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schemas.sql"))
stored_procedure_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stored-procedures"))
with open(env_path, 'r') as file:
    env = json.load(file)

async def connect_db():
    return await asyncpg.connect(
        user=env["db"]["username"],
        port=env["db"]["port"],
        password=env["db"]["password"],
        database=env["db"]["database"],
        host=env["db"]["host"]
    )


async def load_stored_procedures():
    conn = await connect_db()

    with open(schemas_path, 'r', encoding="utf-8") as schemas_sql:
    	try:
    		await conn.execute(schemas_sql.read().strip())
    		print(f"Executed: {schemas_path}")
    	except Exception as e:
    		print(f"Error processing schemas.sql")
    
    for file_name in os.listdir(stored_procedure_directory):
        file_path = os.path.join(stored_procedure_directory, file_name)

        if file_name.endswith(".sql"):
            with open(file_path, 'r', encoding="utf-8") as sql_file:
                sql_content = sql_file.read().strip()
                try:
                    await conn.execute(sql_content)
                    print(f"Executed: {file_name}")
                except Exception as e:
                    print(f"Error executing {file_name}: {e}")

    await conn.close()