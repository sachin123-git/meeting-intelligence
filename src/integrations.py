"""Notion + Trello API wrappers."""
import os
import requests


def push_to_notion(task: str, owner: str = "Unassigned", due_date: str = "", priority: str = "medium") -> dict:
    props = {
        "Name": {"title": [{"text": {"content": task}}]},
        "Owner": {"rich_text": [{"text": {"content": owner}}]},
        "Priority": {"select": {"name": priority}},
    }
    if due_date:
        props["Due"] = {"date": {"start": due_date}}
    r = requests.post(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        json={"parent": {"database_id": os.environ["NOTION_DATABASE_ID"]}, "properties": props},
        timeout=30,
    )
    r.raise_for_status()
    return {"ok": True, "url": r.json().get("url")}


def push_to_trello(task: str, owner: str = "Unassigned", due_date: str = "", priority: str = "medium") -> dict:
    r = requests.post(
        "https://api.trello.com/1/cards",
        params={
            "key": os.environ["TRELLO_KEY"],
            "token": os.environ["TRELLO_TOKEN"],
            "idList": os.environ["TRELLO_LIST_ID"],
            "name": task,
            "desc": f"Owner: {owner}\nPriority: {priority}",
            **({"due": due_date} if due_date else {}),
        },
        timeout=30,
    )
    r.raise_for_status()
    return {"ok": True, "url": r.json().get("shortUrl")}
