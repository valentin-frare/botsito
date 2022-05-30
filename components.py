def row_container(inner_text: str) -> str:
    return f"<div class='row_container'>{inner_text}</div>"

def email(inner_text: str) -> str:
    return f"<div class='email'>{inner_text}</div>"

def last_time(inner_text: str) -> str:
    return f"<div class='last_time'>{inner_text}</div>"

def errors(inner_text: str) -> str:
    return f"<div class='errors'>{inner_text}</div>"

def generations(inner_text: str) -> str:
    return f"<div class='generations'>{inner_text}</div>"

def big_error(inner_text: str) -> str:
    return f"<div class='big_error'>{inner_text}</div>"