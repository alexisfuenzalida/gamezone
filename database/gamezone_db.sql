-- GAMEZONE - respaldo de gamezone_db (MySQL 8.0) con datos de demostración.
-- Importar en una base vacía: mysql -u gamezone_user -p gamezone_db < database/gamezone_db.sql

-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: gamezone_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add Token',7,'add_token'),(26,'Can change Token',7,'change_token'),(27,'Can delete Token',7,'delete_token'),(28,'Can view Token',7,'view_token'),(29,'Can add Token',8,'add_tokenproxy'),(30,'Can change Token',8,'change_tokenproxy'),(31,'Can delete Token',8,'delete_tokenproxy'),(32,'Can view Token',8,'view_tokenproxy'),(33,'Can add perfil',9,'add_perfil'),(34,'Can change perfil',9,'change_perfil'),(35,'Can delete perfil',9,'delete_perfil'),(36,'Can view perfil',9,'view_perfil'),(37,'Can add torneo',10,'add_torneo'),(38,'Can change torneo',10,'change_torneo'),(39,'Can delete torneo',10,'delete_torneo'),(40,'Can view torneo',10,'view_torneo'),(41,'Can add videojuego',11,'add_videojuego'),(42,'Can change videojuego',11,'change_videojuego'),(43,'Can delete videojuego',11,'delete_videojuego'),(44,'Can view videojuego',11,'view_videojuego'),(45,'Can add inscripción',12,'add_inscripcion'),(46,'Can change inscripción',12,'change_inscripcion'),(47,'Can delete inscripción',12,'delete_inscripcion'),(48,'Can view inscripción',12,'view_inscripcion'),(49,'Can add resultado',13,'add_resultado'),(50,'Can change resultado',13,'change_resultado'),(51,'Can delete resultado',13,'delete_resultado'),(52,'Can view resultado',13,'view_resultado');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$Bfs5mbp8oXCJkb5GtyPECj$fB9VQQ6z2OXE+Qw/Xi1SQIZRBa34a9mAqXclmEsxCU0=','2026-10-11 22:19:38.718477',1,'admin_demo','','','',1,1,'2026-10-11 22:18:44.988582'),(2,'pbkdf2_sha256$1000000$M86Z9nPbFzJSBTs2PCpa8a$SMIHRYIgdnXP5tKahQk3+vMlT5jT3+etrkgw2Hcnx7c=',NULL,0,'shadowfox','','','',0,1,'2026-10-11 22:18:45.400998'),(3,'pbkdf2_sha256$1000000$sBTFtEY7cr4DrgE3DE6xI2$EqLByhK3aLtBpxeaOjmPiS+I6JIrCt3xZH4ZtHk9jpo=',NULL,0,'pixelqueen','','','',0,1,'2026-10-11 22:18:45.787938'),(4,'pbkdf2_sha256$1000000$LKDr1FxiCfMse02q8s5t7u$CZqROKlARFf6jZeuipQng8CsbpAwRRD2tFKQz9VN/hE=',NULL,0,'n00bmaster','','','',0,1,'2026-10-11 22:18:46.172034'),(5,'pbkdf2_sha256$1000000$5OhZZYPltyy8SkVRsRhIq8$8Zvb2lH9+knV4rsqTsIDeszbOeXA7hjdEloAu8u2IE0=',NULL,0,'lagkiller','','','',0,1,'2026-10-11 22:18:46.602061'),(6,'pbkdf2_sha256$1000000$Vz6cxRbqqMpcH5oksMKm6Z$RxBcdBwBkcSdvSLqQ783oq2uWwA7bZy8Galjy6HnsAM=',NULL,0,'curicoace','','','',0,1,'2026-10-11 22:18:47.017608'),(7,'pbkdf2_sha256$1000000$0cXf9jJrSlmeTMNecJzuQ2$yPfisdTFJ3kfbu/mRdx3uc+PVgMKvSBbfTKcChNb/bQ=',NULL,0,'frostbyte','','','',0,1,'2026-10-11 22:18:47.401390'),(8,'pbkdf2_sha256$1000000$YhR8ddQ1oGFqP8uSSeUeAH$tN5c83/hXAMUk/9RRxvatQddNDXFwiIjlO7mPbH4r9U=',NULL,0,'neonviper','','','',0,1,'2026-10-11 22:18:47.828730'),(9,'pbkdf2_sha256$1000000$aHnTmyDXQYKj3zk5YRTSVJ$ZnwOUIDvZzj4/DcMuEf9ni+eIuHSBdEw027bg8V2e0o=',NULL,0,'zerocool','','','',0,1,'2026-10-11 22:18:48.206383');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken_token`
--

DROP TABLE IF EXISTS `authtoken_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(7,'authtoken','token'),(8,'authtoken','tokenproxy'),(5,'contenttypes','contenttype'),(6,'sessions','session'),(12,'torneos','inscripcion'),(13,'torneos','resultado'),(10,'torneos','torneo'),(11,'torneos','videojuego'),(9,'usuarios','perfil');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-11 22:18:38.878965'),(2,'auth','0001_initial','2026-10-11 22:18:40.423822'),(3,'admin','0001_initial','2026-10-11 22:18:40.777642'),(4,'admin','0002_logentry_remove_auto_add','2026-10-11 22:18:40.790514'),(5,'admin','0003_logentry_add_action_flag_choices','2026-10-11 22:18:40.803070'),(6,'contenttypes','0002_remove_content_type_name','2026-10-11 22:18:41.093453'),(7,'auth','0002_alter_permission_name_max_length','2026-10-11 22:18:41.231814'),(8,'auth','0003_alter_user_email_max_length','2026-10-11 22:18:41.264373'),(9,'auth','0004_alter_user_username_opts','2026-10-11 22:18:41.275626'),(10,'auth','0005_alter_user_last_login_null','2026-10-11 22:18:41.410105'),(11,'auth','0006_require_contenttypes_0002','2026-10-11 22:18:41.417839'),(12,'auth','0007_alter_validators_add_error_messages','2026-10-11 22:18:41.431603'),(13,'auth','0008_alter_user_username_max_length','2026-10-11 22:18:41.621456'),(14,'auth','0009_alter_user_last_name_max_length','2026-10-11 22:18:41.787292'),(15,'auth','0010_alter_group_name_max_length','2026-10-11 22:18:41.827446'),(16,'auth','0011_update_proxy_permissions','2026-10-11 22:18:41.846404'),(17,'auth','0012_alter_user_first_name_max_length','2026-10-11 22:18:41.999451'),(18,'authtoken','0001_initial','2026-10-11 22:18:42.231765'),(19,'authtoken','0002_auto_20160226_1747','2026-10-11 22:18:42.266598'),(20,'authtoken','0003_tokenproxy','2026-10-11 22:18:42.274358'),(21,'authtoken','0004_alter_tokenproxy_options','2026-10-11 22:18:42.285354'),(22,'sessions','0001_initial','2026-10-11 22:18:42.379171'),(23,'torneos','0001_initial','2026-10-11 22:18:43.287146'),(24,'usuarios','0001_initial','2026-10-11 22:18:43.490452');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `torneos_inscripcion`
--

DROP TABLE IF EXISTS `torneos_inscripcion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `torneos_inscripcion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_inscripcion` datetime(6) NOT NULL,
  `jugador_id` int NOT NULL,
  `torneo_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inscripcion_unica` (`jugador_id`,`torneo_id`),
  KEY `torneos_inscripcion_torneo_id_343c13a1_fk_torneos_torneo_id` (`torneo_id`),
  CONSTRAINT `torneos_inscripcion_jugador_id_ccdf753c_fk_auth_user_id` FOREIGN KEY (`jugador_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `torneos_inscripcion_torneo_id_343c13a1_fk_torneos_torneo_id` FOREIGN KEY (`torneo_id`) REFERENCES `torneos_torneo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `torneos_inscripcion`
--

LOCK TABLES `torneos_inscripcion` WRITE;
/*!40000 ALTER TABLE `torneos_inscripcion` DISABLE KEYS */;
INSERT INTO `torneos_inscripcion` VALUES (1,'2026-10-11 22:18:48.656940',2,1),(2,'2026-10-11 22:18:48.658727',3,1),(3,'2026-10-11 22:18:48.660255',4,1),(4,'2026-10-11 22:18:48.675684',2,2),(5,'2026-10-11 22:18:48.676913',3,2),(6,'2026-10-11 22:18:48.678186',4,2),(7,'2026-10-11 22:18:48.679346',5,2),(8,'2026-10-11 22:18:48.699029',2,3),(9,'2026-10-11 22:18:48.700252',3,3),(10,'2026-10-11 22:18:48.701443',4,3),(11,'2026-10-11 22:18:48.702646',5,3),(12,'2026-10-11 22:18:48.703813',6,3),(13,'2026-10-11 22:18:48.716810',2,4),(14,'2026-10-11 22:18:48.729569',2,5),(15,'2026-10-11 22:18:48.730975',3,5),(16,'2026-10-11 22:18:48.732348',4,5),(17,'2026-10-11 22:18:48.733622',5,5),(18,'2026-10-11 22:18:48.734814',6,5),(19,'2026-10-11 22:18:48.736176',7,5),(20,'2026-10-11 22:18:48.749485',2,6),(21,'2026-10-11 22:18:48.752668',3,6),(22,'2026-10-11 22:18:48.755696',4,6),(23,'2026-10-11 22:18:48.758599',5,6),(24,'2026-10-11 22:18:48.761585',6,6),(25,'2026-10-11 22:18:48.764723',7,6),(26,'2026-10-11 22:18:48.767862',8,6),(27,'2026-10-11 22:18:48.770802',9,6),(28,'2026-10-11 22:18:48.785278',2,7),(29,'2026-10-11 22:18:48.788138',3,7),(30,'2026-10-11 22:18:48.790607',4,7),(31,'2026-10-11 22:18:48.793178',5,7);
/*!40000 ALTER TABLE `torneos_inscripcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `torneos_resultado`
--

DROP TABLE IF EXISTS `torneos_resultado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `torneos_resultado` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `posicion` int unsigned NOT NULL,
  `puntos` int unsigned NOT NULL,
  `inscripcion_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inscripcion_id` (`inscripcion_id`),
  CONSTRAINT `torneos_resultado_inscripcion_id_e54cea5b_fk_torneos_i` FOREIGN KEY (`inscripcion_id`) REFERENCES `torneos_inscripcion` (`id`),
  CONSTRAINT `torneos_resultado_chk_1` CHECK ((`posicion` >= 0)),
  CONSTRAINT `torneos_resultado_chk_2` CHECK ((`puntos` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `torneos_resultado`
--

LOCK TABLES `torneos_resultado` WRITE;
/*!40000 ALTER TABLE `torneos_resultado` DISABLE KEYS */;
INSERT INTO `torneos_resultado` VALUES (1,1,100,20),(2,2,85,21),(3,3,70,22),(4,4,55,23),(5,5,40,24),(6,6,25,25),(7,7,10,26),(8,8,10,27),(9,1,100,28),(10,2,85,29),(11,3,70,30),(12,4,55,31);
/*!40000 ALTER TABLE `torneos_resultado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `torneos_torneo`
--

DROP TABLE IF EXISTS `torneos_torneo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `torneos_torneo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `max_participantes` int unsigned NOT NULL,
  `descripcion` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `videojuego_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `torneos_torneo_videojuego_id_21af3912_fk_torneos_videojuego_id` (`videojuego_id`),
  CONSTRAINT `torneos_torneo_videojuego_id_21af3912_fk_torneos_videojuego_id` FOREIGN KEY (`videojuego_id`) REFERENCES `torneos_videojuego` (`id`),
  CONSTRAINT `torneos_torneo_chk_1` CHECK ((`max_participantes` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `torneos_torneo`
--

LOCK TABLES `torneos_torneo` WRITE;
/*!40000 ALTER TABLE `torneos_torneo` DISABLE KEYS */;
INSERT INTO `torneos_torneo` VALUES (1,'Copa Invierno LoL','2026-10-23 22:00:00.000000',8,'Torneo de League of Legends organizado por GAMEZONE.','DISPONIBLE',1),(2,'Valorant Clash Curicó','2026-10-18 22:00:00.000000',4,'Torneo de Valorant organizado por GAMEZONE.','COMPLETO',2),(3,'FC Masters Primavera','2026-10-31 22:00:00.000000',16,'Torneo de EA Sports FC 26 organizado por GAMEZONE.','DISPONIBLE',3),(4,'Street Fighter Showdown','2026-10-14 22:00:00.000000',8,'Torneo de Street Fighter 6 organizado por GAMEZONE.','DISPONIBLE',4),(5,'Rocket League Rumble','2026-10-11 22:00:00.000000',6,'Torneo de Rocket League organizado por GAMEZONE.','EN_CURSO',5),(6,'Liga Relámpago Valorant','2026-09-26 22:00:00.000000',8,'Torneo de Valorant organizado por GAMEZONE.','FINALIZADO',2),(7,'Torneo Apertura LoL','2026-09-01 23:00:00.000000',4,'Torneo de League of Legends organizado por GAMEZONE.','FINALIZADO',1);
/*!40000 ALTER TABLE `torneos_torneo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `torneos_videojuego`
--

DROP TABLE IF EXISTS `torneos_videojuego`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `torneos_videojuego` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `torneos_videojuego`
--

LOCK TABLES `torneos_videojuego` WRITE;
/*!40000 ALTER TABLE `torneos_videojuego` DISABLE KEYS */;
INSERT INTO `torneos_videojuego` VALUES (3,'EA Sports FC 26'),(1,'League of Legends'),(5,'Rocket League'),(4,'Street Fighter 6'),(2,'Valorant');
/*!40000 ALTER TABLE `torneos_videojuego` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_perfil`
--

DROP TABLE IF EXISTS `usuarios_perfil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_perfil` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rol` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `usuarios_perfil_usuario_id_ca6ea2f9_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_perfil`
--

LOCK TABLES `usuarios_perfil` WRITE;
/*!40000 ALTER TABLE `usuarios_perfil` DISABLE KEYS */;
INSERT INTO `usuarios_perfil` VALUES (1,'ADMIN',1),(2,'JUGADOR',2),(3,'JUGADOR',3),(4,'JUGADOR',4),(5,'JUGADOR',5),(6,'JUGADOR',6),(7,'JUGADOR',7),(8,'JUGADOR',8),(9,'JUGADOR',9);
/*!40000 ALTER TABLE `usuarios_perfil` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-11 22:20:44
