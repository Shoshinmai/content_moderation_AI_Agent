from pydantic import BaseModel
import google.generativeai as genai
import json
import re
import time
import pandas as pd
from colorama import Fore, Back, Style, init
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
from typing import List

load_dotenv()

init(autoreset=True)

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

Moderation_table = "Moderation_table"

def supabase_operation(operation, data=None, filters=None):
    query = supabase.table(Moderation_table)

    if operation == "insert":
        query = query.insert(data)
    elif operation == "select":
        query = query.select("*")
    elif operation == "update":
        query = query.update(data)
    elif operation == "delete":
        query = query.delete()
    else:
        raise ValueError("Unsupported operation")

    if filters:
        for column, operator, value in filters:
            if operator == "eq":
                query = query.eq(column, value)
            elif operator == "gt":
                query = query.gt(column, value)
            elif operator == "lt":
                query = query.lt(column, value)
            elif operator == "like":
                query = query.like(column, value)

    return query.execute()