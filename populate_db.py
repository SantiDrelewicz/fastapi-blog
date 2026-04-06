import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import delete, select, update

import models
from database import AsyncSessionLocal, engine
from image_utils import PROFILE_PICS_DIR
from main import app


POPULATE_IMAGES_DIR = Path("populate_images")

USERS = [
    {
        "username": "usuario_uno",
        "email": "usuario_uno@ejemplo.com",
        "password": "ClaveSegura1",
        "image_name": "willow.png"
    },
    {
        "username": "usuario_dos",
        "email": "usuario_dos@ejemplo.com",
        "password": "MiPassword2",
        "image_name": "maradona.png"
    },
    {
        "username": "usuario_tres",
        "email": "usuario_tres@ejemplo.com",
        "password": "Seguridad123",
        "image_name": "poppy.png"
    },
    {
        "username": "usuario_cuatro",
        "email": "usuario_cuatro@ejemplo.com",
        "password": "ClaveAlpha9",
        "image_name": "bronx.png"
    },
    {
        "username": "usuario_cinco",
        "email": "usuario_cinco@ejemplo.com",
        "password": "PruebaPass88",
        "image_name": "farmdogs.png"
    },
    {
        "username": "usuario_seis",
        "email": "usuario_seis@ejemplo.com",
        "password": "OtraClave77",
        # no image - uses default
    }
]

POSTS = [
    {
        "title": "Introducción a Python",
        "content": "Python es un lenguaje versátil y fácil de aprender ideal para principiantes."
    },
    {
        "title": "Variables y tipos de datos",
        "content": "Las variables permiten almacenar información como números, texto y booleanos."
    },
    {
        "title": "Estructuras de control",
        "content": "Los if, for y while permiten controlar el flujo de ejecución de un programa."
    },
    {
        "title": "Funciones en Python",
        "content": "Las funciones ayudan a reutilizar código y organizar mejor los programas."
    },
    {
        "title": "Listas y tuplas",
        "content": "Las listas son mutables mientras que las tuplas son inmutables."
    },
    {
        "title": "Diccionarios",
        "content": "Los diccionarios almacenan pares clave-valor y son muy útiles para datos estructurados."
    },
    {
        "title": "Manejo de errores",
        "content": "Se pueden usar try y except para manejar errores en tiempo de ejecución."
    },
    {
        "title": "Lectura de archivos",
        "content": "Python permite leer archivos de texto fácilmente con open()."
    },
    {
        "title": "Escritura de archivos",
        "content": "También se pueden escribir datos en archivos usando modos como 'w' o 'a'."
    },
    {
        "title": "Comprensiones de listas",
        "content": "Permiten crear listas de forma concisa y eficiente."
    },
    {
        "title": "Programación orientada a objetos",
        "content": "Las clases permiten modelar objetos con atributos y métodos."
    },
    {
        "title": "Herencia en clases",
        "content": "La herencia permite reutilizar código entre clases relacionadas."
    },
    {
        "title": "Decoradores",
        "content": "Los decoradores permiten modificar funciones sin cambiar su código."
    },
    {
        "title": "Módulos y paquetes",
        "content": "Se pueden organizar los proyectos en módulos y paquetes reutilizables."
    },
    {
        "title": "Uso de pip",
        "content": "pip permite instalar y gestionar dependencias en Python."
    },
    {
        "title": "Entornos virtuales",
        "content": "Permiten aislar dependencias entre distintos proyectos."
    },
    {
        "title": "Introducción a NumPy",
        "content": "NumPy facilita el trabajo con arreglos y operaciones matemáticas."
    },
    {
        "title": "Introducción a pandas",
        "content": "pandas es ideal para análisis de datos estructurados."
    },
    {
        "title": "Series en pandas",
        "content": "Una Serie es una estructura unidimensional etiquetada."
    },
    {
        "title": "DataFrames en pandas",
        "content": "Un DataFrame es una tabla bidimensional con etiquetas."
    },
    {
        "title": "Filtrado de datos",
        "content": "Se pueden filtrar datos en pandas usando condiciones booleanas."
    },
    {
        "title": "Agrupamiento de datos",
        "content": "groupby permite agrupar y resumir información."
    },
    {
        "title": "Visualización con matplotlib",
        "content": "Permite crear gráficos como líneas, barras e histogramas."
    },
    {
        "title": "Introducción a seaborn",
        "content": "Seaborn simplifica la creación de gráficos estadísticos."
    },
    {
        "title": "APIs con FastAPI",
        "content": "FastAPI permite crear APIs rápidas y eficientes en Python."
    },
    {
        "title": "Validación con Pydantic",
        "content": "Pydantic ayuda a validar datos usando modelos."
    },
    {
        "title": "Bases de datos SQLite",
        "content": "SQLite es una base de datos ligera integrada en Python."
    },
    {
        "title": "ORM con SQLAlchemy",
        "content": "SQLAlchemy permite interactuar con bases de datos usando objetos."
    },
    {
        "title": "Migraciones con Alembic",
        "content": "Alembic facilita la gestión de cambios en la base de datos."
    },
    {
        "title": "Autenticación básica",
        "content": "Se puede implementar autenticación con usuarios y contraseñas."
    },
    {
        "title": "JWT en APIs",
        "content": "Los tokens JWT permiten autenticación segura en APIs."
    },
    {
        "title": "Hash de contraseñas",
        "content": "Es importante almacenar contraseñas de forma segura usando hashing."
    },
    {
        "title": "Pruebas unitarias",
        "content": "Permiten verificar que cada parte del código funcione correctamente."
    },
    {
        "title": "Uso de pytest",
        "content": "pytest es una herramienta popular para testing en Python."
    },
    {
        "title": "Logging",
        "content": "El logging permite registrar eventos durante la ejecución."
    },
    {
        "title": "Buenas prácticas",
        "content": "Seguir convenciones mejora la legibilidad y mantenimiento del código."
    },
    {
        "title": "PEP8",
        "content": "PEP8 define el estilo de código recomendado en Python."
    },
    {
        "title": "Documentación",
        "content": "Es importante documentar funciones y módulos correctamente."
    },
    {
        "title": "Control de versiones",
        "content": "Git permite llevar un historial de cambios del código."
    },
    {
        "title": "Trabajo en equipo",
        "content": "Las herramientas colaborativas facilitan el desarrollo conjunto."
    },
    {
        "title": "Deploy de aplicaciones",
        "content": "Se pueden desplegar apps en servidores o servicios cloud."
    },
    {
        "title": "Docker básico",
        "content": "Docker permite empaquetar aplicaciones en contenedores."
    },
    {
        "title": "Optimización de código",
        "content": "Mejorar el rendimiento es clave en aplicaciones grandes."
    },
    {
        "title": "Seguridad en aplicaciones",
        "content": "Es fundamental proteger datos y accesos en sistemas."
    }
]

# The 44th post - always the oldest (easter egg for pagination tutorial)
POST_45 = {
    "title": "La pasión del fútbol argentino",
    "content": "El fútbol argentino se caracteriza por su intensidad, historia y la pasión de los hinchas, siendo una parte fundamental de la cultura del país."
}



async def clear_existing_data() -> None:
    # Delete profile pictures from local storage
    if PROFILE_PICS_DIR.exists():
        for file in PROFILE_PICS_DIR.iterdir():
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        print(f"Deleted profile pictures from {PROFILE_PICS_DIR}")

    # Clear database tables (order respects foreign keys)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()
    print("Cleared existing data")


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Post).order_by(models.Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # First post (POST_44) is the oldest - ~90 days ago
        await db.execute(
            update(models.Post)
            .where(models.Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        # Remaining posts: each ~1.5 days newer than previous
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def populate() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        # Clear existing data (local images first, then database)
        await clear_existing_data()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:
            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"  Created: {user['username']}")

            response = await client.post(
                "/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                image_path = POPULATE_IMAGES_DIR / image_name
                if image_path.exists():
                    response = await client.patch(
                        f"/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                image_name,
                                image_path.read_bytes(),
                                "image/png",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"    Uploaded: {image_name}")

            users.append(
                {"id": user["id"], "username": user["username"], "token": token},
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_44 (will become oldest after date update)
        response = await client.post(
            "/api/posts",
            json={"title": POST_44["title"], "content": POST_44["content"]},
            headers={"Authorization": f"Bearer {users[0]['token']}"},
        )
        response.raise_for_status()
        print(f"  Created: '{POST_44['title']}'")

        # Create remaining posts in reverse (last in list = oldest, first = newest)
        for i, post_data in enumerate(reversed(POSTS)):
            user = users[i % len(users)]
            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                f"  Created: '{title[:50]}...'"
                if len(title) > 50
                else f"  Created: '{title}'",
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Profile pictures saved locally")


if __name__ == "__main__":
    asyncio.run(populate())