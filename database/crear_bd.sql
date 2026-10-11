-- GAMEZONE - crea la base de datos y un usuario dedicado (ejecutar como root).
-- Cambia la contraseña y usa la misma en el archivo .env (DB_PASSWORD).

CREATE DATABASE IF NOT EXISTS gamezone_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'gamezone_user'@'localhost' IDENTIFIED BY 'cambia_esta_clave';
CREATE USER IF NOT EXISTS 'gamezone_user'@'%' IDENTIFIED BY 'cambia_esta_clave';

GRANT ALL PRIVILEGES ON gamezone_db.* TO 'gamezone_user'@'localhost';
GRANT ALL PRIVILEGES ON gamezone_db.* TO 'gamezone_user'@'%';
-- Solo necesario para ejecutar las pruebas automáticas (manage.py test):
GRANT ALL PRIVILEGES ON test_gamezone_db.* TO 'gamezone_user'@'localhost';
GRANT ALL PRIVILEGES ON test_gamezone_db.* TO 'gamezone_user'@'%';

FLUSH PRIVILEGES;
