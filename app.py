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

class ModerationResult(BaseModel):
    is_offensive: bool
    confidence_score: float
    flagged_terms: list[str]

class ModerationOutput(BaseModel):
    content_id: str
    content: str
    status: str
    is_offensive: bool
    confidence_score: float
    flagged_terms: List[str]
    created_at: str
    
def moderate_text(content_id: str, content: str) -> dict:
    offensive_terms = ["badword1", "badword2", "offensivephrase"]
    flagged_terms = [
        term
        for term in offensive_terms
        if re.search(r"\b" + re.escape(term) + r"\b", content, re.IGNORECASE)
    ]
    is_offensive = len(flagged_terms) > 0
    confidence_score = 0.9 if is_offensive else 0.1  # Simplified confidence score

    result = {
        "content_id": content_id,
        "content": content,
        "status": "moderated",
        "is_offensive": is_offensive,
        "confidence_score": confidence_score,
        "flagged_terms": flagged_terms,  # Keep as a list
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        supabase_operation("insert", data=result)
        print(f"{Fore.GREEN}✅ Moderation result saved to database.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error saving to database: {e}{Style.RESET_ALL}")

    return result