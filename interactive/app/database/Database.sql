-- MySQL Workbench Synchronization
-- Generated: 2020-02-16 13:36
-- Model: New Model
-- Version: 1.0
-- Project: Name of the project
-- Author: verma

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

ALTER TABLE `a1_db`.`user_has_imgs` 
DROP FOREIGN KEY `fk_user_has_imgs_imgs1`;

ALTER TABLE `a1_db`.`user_has_imgs` 
DROP FOREIGN KEY `fk_user_has_imgs_userinfo`;

ALTER TABLE `a1_db`.`user_has_imgs` ADD CONSTRAINT `fk_user_has_imgs_userinfo`
  FOREIGN KEY (`userinfo_UserID`)
  REFERENCES `a1_db`.`userinfo` (`UserID`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION,
ADD CONSTRAINT `fk_user_has_imgs_imgs1`
  FOREIGN KEY (`imgs_ImgID`)
  REFERENCES `a1_db`.`imgs` (`ImgID`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
