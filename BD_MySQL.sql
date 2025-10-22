-- --------------------------------------------------------
-- Servidor:                     127.0.0.1
-- Versão do servidor:           8.4.4 - MySQL Community Server - GPL
-- OS do Servidor:               Win64
-- HeidiSQL Versão:              12.10.0.7000
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Copiando estrutura do banco de dados para sistema_usuario
CREATE DATABASE IF NOT EXISTS `sistema_usuario` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `sistema_usuario`;

-- Copiando estrutura para tabela sistema_usuario.roles
CREATE TABLE IF NOT EXISTS `roles` (
  `roleid` int NOT NULL AUTO_INCREMENT,
  `rolename` varchar(50) NOT NULL,
  PRIMARY KEY (`roleid`),
  UNIQUE KEY `rolename` (`rolename`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Copiando estrutura para tabela sistema_usuario.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password` varchar(255) NOT NULL,
  `roleid` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `roleid` (`roleid`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`roleid`) REFERENCES `roles` (`roleid`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Copiando estrutura para tabela sistema_usuario.usuario_roles
CREATE TABLE IF NOT EXISTS `usuario_roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuarioid` int NOT NULL,
  `roleid` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usuarioid` (`usuarioid`),
  KEY `roleid` (`roleid`),
  CONSTRAINT `usuario_roles_ibfk_1` FOREIGN KEY (`usuarioid`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `usuario_roles_ibfk_2` FOREIGN KEY (`roleid`) REFERENCES `roles` (`roleid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Copiando estrutura para procedure sistema_usuario.login_user
DELIMITER //
CREATE PROCEDURE `login_user`(
	IN `p_username` VARCHAR(255),
	IN `p_password` VARCHAR(255),
	OUT `login_success` TINYINT(1),
	OUT `message` TEXT,
	OUT `p_email` VARCHAR(255)
)
BEGIN
	DECLARE stored_password VARCHAR(255);
	DECLARE stored_email VARCHAR(255);
	DECLARE password_match TINYINT(1);
	
	-- Verificar si el usuario existe utilizando la función user_exists
	IF user_exists(p_username) = 0 THEN
		SET login_success = 0;
		SET message = CONCAT('El usuario "', p_username, '" no existe.');
	ELSE
	
		-- Si el usuario existe, obtener la contraseña cifrada almacenada
		SELECT password, email 
		INTO stored_password, stored_email
		FROM usuarios
		WHERE username = p_username;
	
		-- Verificar si se obtuvo una contraseña almacenada
		IF stored_password IS NULL THEN
			SET login_success = 0;
			SET message = 'Error al obtener la contraseña del usuario.';
		ELSE
			SET login_success = 1;
			SET message = 'Usuario encontrado, Realiza la comparación en el backend.';
			SET p_email = stored_email;
		END IF;
	END IF;

END//
DELIMITER ;

-- Copiando estrutura para procedure sistema_usuario.register_user
DELIMITER //
CREATE PROCEDURE `register_user`(
	IN `p_email` VARCHAR(255),
	IN `p_username` VARCHAR(50),
	IN `p_password_hash` VARCHAR(255),
	IN `p_roleid` INT
)
BEGIN

	DECLARE new_user_id INT;
	
	-- Declarar manejador de excepciones para errores
	DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
	BEGIN
		-- Revierte cualquier cambio si ocurre un error
		ROLLBACK;
		-- Devuelve cualquier cambio si ocurre un error
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'Error al insertar el usuario: ';
	END;
	
	-- Iniciar la transacción
	START TRANSACTION;
	
	-- Verifica si el usuario ya existe
	IF EXISTS (SELECT 1 FROM usuarios WHERE username = p_username) THEN
		-- Errir: Usuario ya existe
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'El nombre de usuario ya existe';
		
	-- Verifica si el rol existe
	ELSEIF NOT EXISTS (SELECT 1 FROM roles WHERE roleid = p_roleid) THEN
		-- Error: Rol no existe
		SIGNAL SQLSTATE '45000'
		SET MESSAGE_TEXT = 'El rol no existe';		
		
	ELSE
		
		-- Insertar el nuevo usuario
		SET new_user_id = insert_user(p_email, p_username, p_password_hash, p_roleid);
		
		-- Insertar en la tabla usuarios_roles con el id del usuario y el id del rol
		INSERT INTO usuario_roles (usuarioid, roleid)
		VALUES (new_user_id, p_roleid);
		
		-- Confirmar la transacción
		COMMIT;
		
		-- Retornar mensaje de éxito y el ID del nuevo usuario
		SELECT 'Usuario registrado correctamente.', new_user_id;
		
	END IF;
END//
DELIMITER ;

-- Copiando estrutura para procedure sistema_usuario.update_password
DELIMITER //
CREATE PROCEDURE `update_password`(
	IN `p_email` VARCHAR(255),
	IN `p_password_hash` VARCHAR(255)
)
BEGIN
	DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
	BEGIN
		SELECT 'Error en la actualización de la contraseña.' AS Error_Message;
	END;
	
	-- Actualizando la contraseña
	UPDATE usuarios
	SET password = p_password_hash
	WHERE email = p_email;
	
	-- Verifica si se actualizó alguna fila
	IF ROW_COUNT() = 0 THEN 
		SELECT 'No se encontró el correo electrónico.' AS Error_Message;
	ELSE
		SELECT 'Contraseña actualizada correctamente.' AS Error_Message;
	END IF;
END//
DELIMITER ;

-- Copiando estrutura para função sistema_usuario.get_encrypted_password
DELIMITER //
CREATE FUNCTION `get_encrypted_password`(
	`p_username` VARCHAR(255)
) RETURNS varchar(255) CHARSET utf8mb4
    DETERMINISTIC
BEGIN
	DECLARE stored_password VARCHAR(255);
	
	-- Verificamos si el usuario existe
	IF user_exists(p_username) = 0 THEN
		RETURN NULL; -- Si no existe, retornamos NULL
	ELSE
	
		-- Obtener la contraseña cifrada del usuario
		SELECT password INTO stored_password
		FROM usuarios
		WHERE username = p_username;
		RETURN stored_password;
	END IF;
END//
DELIMITER ;

-- Copiando estrutura para função sistema_usuario.insert_user
DELIMITER //
CREATE FUNCTION `insert_user`(
	`p_email` VARCHAR(255),
	`p_username` VARCHAR(255),
	`p_password_hash` VARCHAR(255),
	`p_roleid` INT
) RETURNS int
    DETERMINISTIC
BEGIN
	DECLARE user_id INT;
	
	-- Inserta el nuevo usuario
	INSERT INTO usuarios (email, username, password, roleid)
	VALUES (p_email, p_username, p_password_hash, p_roleid);
	
	-- Retorna el ID del usuario insertado
	SET user_id = LAST_INSERT_ID();
	
	RETURN user_id;
END//
DELIMITER ;

-- Copiando estrutura para função sistema_usuario.user_exists
DELIMITER //
CREATE FUNCTION `user_exists`(
	`p_username` VARCHAR(255)
) RETURNS tinyint(1)
    DETERMINISTIC
BEGIN
	DECLARE result TINYINT(1);
	
	-- Verificar si el usuario existe en la base de datos
	SELECT COUNT(*) INTO result
	FROM usuarios
	WHERE username = p_username;
	
	-- Si el resultado es mayor que 0, el usuario existe
	IF result > 0 THEN
		RETURN 1; -- Usuario existe
	ELSE
		RETURN 0; -- Usuario no existe
	END IF;
	
 END//
DELIMITER ;

-- Copiando estrutura para função sistema_usuario.user_exists_by_email
DELIMITER //
CREATE FUNCTION `user_exists_by_email`(
	`p_email` TEXT
) RETURNS tinyint(1)
    DETERMINISTIC
BEGIN
	-- Verifica si el correo electrónico existe en la tabla de usuarios
	IF EXISTS (SELECT 1 FROM usuarios WHERE email = p_email) THEN
		RETURN TRUE; -- El correo electrónico existe
	ELSE
		RETURN FALSE; -- El correo electrónico no existe
	END IF;
	
	
END//
DELIMITER ;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
