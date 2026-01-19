import base64, json, datetime

def encode_cursor(created_at: datetime, id: int) -> str:
    cursor_dict = {
        "created_at": created_at.isoformat(),  # ✅ stringify
        "id": id,
    }

    raw = json.dumps(cursor_dict, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")

def decode_cursor(cursor: str):
    raw = base64.urlsafe_b64decode(cursor.encode("ascii"))
    data = json.loads(raw.decode("utf-8"))
    return (
        datetime.datetime.fromisoformat(data["created_at"]),
        data["id"],
    )