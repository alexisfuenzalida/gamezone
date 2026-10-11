# GAMEZONE · Plataforma de Torneos Gamer

Evaluación Sumativa N°3 · Programación Back End (TI3V41) · INACAP Sede Curicó · Primavera 2026

Plataforma web para gestionar torneos de videojuegos: registro de jugadores, administración de torneos,
inscripciones, estados, resultados, informes y una API REST.

**Tecnologías:** Python 3.10+ · Django 5.2 LTS · MySQL 8.0 · Django REST Framework · Bootstrap 5.3

## Instalación

```bash
python -m venv venv
venv\Scripts\activate                 # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

mysql -u root -p < database/crear_bd.sql   # crea la base gamezone_db y el usuario gamezone_user
copy .env.example .env                     # editar DB_PASSWORD (la de crear_bd.sql) y DJANGO_SECRET_KEY

python manage.py migrate
python manage.py cargar_demo               # datos de demostración
python manage.py runserver
```

Abrir **http://127.0.0.1:8000/**

Si los datos de demostración quedaron con fechas pasadas, `python manage.py cargar_demo --reiniciar` los vuelve a crear con fechas a partir de hoy.

En vez de `migrate` y `cargar_demo`, también se puede importar el respaldo:
`mysql -u gamezone_user -p gamezone_db < database/gamezone_db.sql`

### Usuarios de demostración (contraseña `Gamezone2026!`)

| Usuario | Rol |
|---|---|
| `admin_demo` | Administrador (también entra al panel `/admin/`) |
| `shadowfox`, `pixelqueen`, `neonviper` y otros | Jugador |

## Funcionalidades

- **Torneos (Administrador):** crear, editar (incluido el estado), eliminar con confirmación.
- **Listado:** filtros por videojuego, fecha, estado y mínimo de inscritos. El detalle muestra a los inscritos y sus resultados.
- **Validaciones:** viven en `Torneo.clean()` y las comparten el formulario web y la API.
  - El nombre tiene al menos 5 caracteres y no puede repetirse.
  - La fecha no puede estar en el pasado.
  - El máximo de participantes va de 2 a 128, y no puede quedar por debajo de los inscritos que ya hay.
- **Sesiones y roles:** login y registro de jugadores. Las vistas de administrador usan el decorador `solo_admin`, que responde 403 si no corresponde.
- **Inscripciones:**
  - Un jugador no puede inscribirse dos veces en el mismo torneo. Lo valida el código y también la base de datos, con `UniqueConstraint`.
  - Solo se puede inscribir en torneos Disponibles, con cupo y que aún no comiencen.
- **Estados:** Disponible, Completo, En Curso y Finalizado. El torneo pasa solo a *Completo* al llenarse los cupos; el resto de los cambios los hace el administrador.
- **Resultados:** el administrador registra la posición y los puntos de cada inscrito.
- **Informes:** torneos totales, realizados y finalizados; inscritos por torneo; torneos con mayor participación; ranking de jugadores.
- **Errores:** páginas propias 404, 403 y 500 (se ven con `DJANGO_DEBUG=False`) y mensajes claros para las inscripciones no válidas.

## API REST

Autenticación por token. `POST /api/token/` con `username` y `password` devuelve un token, que se envía en el header `Authorization: Token <token>`.

| Método | Endpoint | Permiso |
|---|---|---|
| GET | `/api/torneos/` (filtros `videojuego`, `estado`, `fecha`, `min_inscritos`) · `/api/torneos/{id}/` | Autenticado |
| POST · PUT · PATCH · DELETE | `/api/torneos/` · `/api/torneos/{id}/` | Administrador |
| POST | `/api/torneos/{id}/inscribirse/` | Jugador |

Hay una colección de Postman en `docs/GAMEZONE_API.postman_collection.json`; sus peticiones se ejecutan en orden.

## Pruebas

```bash
python manage.py test
```

## Estructura

```
gamezone/   settings.py (MySQL, sesiones, DRF) y urls.py raíz
torneos/    models.py (validaciones e inscripción), forms.py, views.py, urls.py, informes.py, templates/
usuarios/   Perfil con rol, registro y decorador solo_admin
api/        serializers.py, views.py, permissions.py, urls.py
templates/  base.html, login, registro y páginas de error
static/     css/gamezone.css
database/   crear_bd.sql y respaldo gamezone_db.sql
```
