# GAMEZONE · Plataforma de Torneos Gamer

Evaluación Sumativa N°3 · Programación Back End (TI3V41) · INACAP Sede Curicó · Primavera 2026

Plataforma web para gestionar torneos de videojuegos: registro de jugadores, administración de torneos,
inscripciones, seguimiento de estados y resultados, informes y una API REST.

**Tecnologías:** Python 3.10+ (probado con 3.14) · Django 5.2 LTS · MySQL 8.0 · Django REST Framework 3.18 · Bootstrap 5.3

---

## 1. Instalación

### Requisitos
- Python 3.10 o superior
- MySQL 8.0 o superior

### Pasos

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la base de datos y el usuario (como root de MySQL)
mysql -u root -p < database/crear_bd.sql

# 4. Configurar las variables de entorno
copy .env.example .env         # Windows  (cp en Linux / macOS)
#    Editar .env: DB_PASSWORD debe ser la misma clave usada en crear_bd.sql
#    y DJANGO_SECRET_KEY debe ser una clave nueva.
```

**5. Cargar los datos.** Elige una de estas dos opciones:

| Opción A: migraciones + datos de demostración | Opción B: importar el respaldo SQL |
|---|---|
| `python manage.py migrate` | `mysql -u gamezone_user -p gamezone_db < database/gamezone_db.sql` |
| `python manage.py cargar_demo` | |

> `python manage.py cargar_demo --reiniciar` vuelve a crear los torneos con fechas relativas al día actual
> (útil si los datos de demostración quedaron con fechas pasadas).

```bash
# 6. Iniciar el servidor
python manage.py runserver
```

Abrir **http://127.0.0.1:8000/**

### Usuarios de demostración

Todos usan la contraseña **`Gamezone2026!`**

| Usuario | Rol | Uso |
|---|---|---|
| `admin_demo` | Administrador (superusuario) | Gestionar torneos y estados, resultados, informes, panel `/admin/` |
| `shadowfox`, `pixelqueen`, `n00bmaster`, `lagkiller`, `curicoace`, `frostbyte`, `neonviper`, `zerocool` | Jugador | Inscribirse, cancelar inscripción, ver "Mis torneos" |

También se puede crear una cuenta nueva de jugador en **Crear cuenta**.

---

## 2. Funcionalidades

### Visitante (sin sesión)
- Ver la página de inicio con el resumen de torneos, el listado con filtros y el detalle de cada torneo.
- Registrarse como jugador e iniciar sesión.

### Jugador
- Inscribirse en torneos **Disponibles**. El sistema impide inscribirse dos veces, en un torneo lleno o en uno que ya comenzó.
- Cancelar su inscripción mientras el torneo no haya comenzado.
- **Mis torneos**: sus inscripciones, con la posición, los puntos y las partidas de cada torneo.

### Administrador
- **CRUD de torneos**: crear, editar, eliminar (con confirmación; no se puede eliminar un torneo En Curso).
- **Estados**: Disponible → Completo → En Curso → Finalizado.
  - Pasa a *Completo* solo al llenarse los cupos, y vuelve a *Disponible* si se libera uno.
  - Para pasar a *En Curso* o *Finalizado* se necesitan al menos 2 jugadores.
  - Para *Finalizar* todos los inscritos deben tener su resultado.
  - Un torneo *Finalizado* no puede volver a un estado anterior.
- **Resultados**: registra la posición, los puntos y las partidas ganadas y jugadas de cada inscrito (sin posiciones repetidas).
- Quitar a un jugador de un torneo.
- **Informes**: torneos totales, realizados y finalizados; inscritos por torneo; torneos con mayor participación; participación por videojuego; ranking de jugadores.

### Validaciones del formulario de torneos
- El nombre es obligatorio, tiene al menos 5 caracteres y no puede repetirse (sin importar mayúsculas).
- La fecha no puede estar en el pasado.
- El máximo de participantes va de 2 a 128, y al editar no puede quedar por debajo de los inscritos que ya hay.
- Los errores se muestran junto a cada campo y el campo se marca en rojo.

### Manejo de errores
- Páginas propias para los errores **404, 403, 400 y 500**, y para el error de seguridad CSRF. Solo se ven con `DJANGO_DEBUG=False`; para probarlas en local, usar `runserver --insecure`.
- Las inscripciones no válidas se informan con un mensaje claro.
- Los errores del servidor quedan registrados en `logs/errores.log`.

---

## 3. API REST

Base: `http://127.0.0.1:8000/api/`. Las respuestas son JSON y se pueden explorar en el navegador (API navegable de DRF).

**Autenticación:** `POST /api/token/` con `username` y `password` devuelve un token, que se envía en el header
`Authorization: Token <token>`. La API también acepta la sesión iniciada en el navegador.

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| POST | `/api/token/` | Público | Obtener token |
| GET | `/api/torneos/` | Autenticado | Lista paginada con filtros: `q`, `videojuego`, `estado`, `fecha_desde`, `fecha_hasta`, `min_inscritos`, `max_inscritos`, `orden` |
| GET | `/api/torneos/{id}/` | Autenticado | Detalle con inscritos y resultados |
| POST / PUT / PATCH / DELETE | `/api/torneos/` · `/api/torneos/{id}/` | Administrador | Crear, actualizar o eliminar |
| POST / DELETE | `/api/torneos/{id}/inscripcion/` | Jugador | Inscribirse o cancelar la inscripción |
| GET | `/api/torneos/{id}/inscritos/` | Autenticado | Jugadores inscritos |
| GET | `/api/inscripciones/` | Autenticado | El jugador ve las suyas; el administrador ve todas |
| GET (escritura: admin) | `/api/videojuegos/` | Autenticado | Catálogo de videojuegos |
| GET | `/api/informes/` | Administrador | Estadísticas de la plataforma |

**Códigos de respuesta:**
- `400`: datos inválidos, con el detalle de cada campo.
- `401`: no hay autenticación.
- `403`: el usuario no tiene permiso.
- `404`: el recurso no existe.
- `409`: se intentó eliminar un torneo En Curso.

**Postman:** importar `docs/GAMEZONE_API.postman_collection.json` y ejecutar primero la carpeta *1. Autenticación*,
que guarda los tokens y los ids en variables de la colección.

---

## 4. Pruebas automáticas

```bash
python manage.py test
```

Son 68 pruebas: CRUD, validaciones, filtros, permisos por rol, inscripciones, resultados, páginas de error, API e informes.
Django crea una base temporal `test_gamezone_db`; el script `crear_bd.sql` ya incluye el permiso necesario.

---

## 5. Estructura del proyecto

```
gamezone/            Configuración: settings (MySQL, sesiones, DRF, logging) y urls raíz
torneos/             App principal
  models.py          Videojuego, Torneo, Inscripcion, Resultado
  reglas.py          Reglas de negocio compartidas por la web y la API (nombre, fecha, estados)
  servicios.py       Inscribir, cancelar, validar eliminación (con bloqueo de cupos concurrente)
  informes.py        Estadísticas con consultas agregadas
  forms.py           Formularios de torneo, filtros y resultados
  views.py · urls.py Vistas web y rutas
  signals.py         Cambio automático Disponible ↔ Completo
  management/commands/cargar_demo.py
usuarios/            Perfil (rol Jugador/Administrador), registro y decorador solo_admin
api/                 Serializers, viewsets, permisos y rutas de la API REST
templates/           base.html, login, registro y páginas de error
static/css/          Estilos propios (gamezone.css)
database/            crear_bd.sql y respaldo gamezone_db.sql
docs/                Colección de Postman
```

## 6. Dónde se cumple cada criterio de evaluación

| # | Criterio | Implementación |
|---|---|---|
| 1 | Proyecto Django configurado | `gamezone/settings.py`: credenciales en `.env`, idioma y zona horaria de Chile, sesiones seguras |
| 2 | MySQL configurado y conectado | Motor `mysql` en `settings.py`, usuario dedicado (`database/crear_bd.sql`), `utf8mb4`, conexiones persistentes |
| 3 | CRUD de torneos | `torneos/views.py`: `crear`, `lista`, `detalle`, `editar`, `eliminar` (más la API) |
| 4 | Formulario de creación | `torneos/templates/torneos/form.html` + `TorneoForm` |
| 5 | Listado con detalles | `lista.html` (filtros y paginación) y `detalle.html` (inscritos y resultados) |
| 6 | Plantilla base responsiva | `templates/base.html` con Bootstrap 5 y estilos propios |
| 7 | Inicio con resumen | `inicio.html`: cifras, torneos en vivo y próximos torneos |
| 8 | Rutas en urls.py | `gamezone/urls.py`, `torneos/urls.py`, `usuarios/urls.py`, `api/urls.py` (rutas con nombre) |
| 9 | Validación de formularios | `TorneoForm` + `torneos/reglas.py` (crear y editar) |
| 10 | Manejo de errores | Páginas 404/403/400/500, mensajes de inscripción no válida, `get_object_or_404`, logging |
