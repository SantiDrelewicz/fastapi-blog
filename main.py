from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


POSTS: list[dict[str, int | str]] = [
    {
        "id": 1,
        "author": "Santi Drelewicz",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "January 2, 2026",
    },
    {
        "id": 2,
        "author": "John Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "January 2, 2026",
    },
]



@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{POSTS[0]['title']}</h1>"


@app.get("/api/posts")
def get_posts():
    return POSTS
