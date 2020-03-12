-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema a1_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema a1_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `a1_db` DEFAULT CHARACTER SET utf8 ;
USE `a1_db` ;

-- -----------------------------------------------------
-- Table `a1_db`.`userinfo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `a1_db`.`userinfo` (
  `UserID` INT NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(100) NOT NULL,
  `Hashedpassword` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE INDEX `UserID_UNIQUE` (`UserID` ASC),
  UNIQUE INDEX `Username_UNIQUE` (`Username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `a1_db`.`imgs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `a1_db`.`imgs` (
  `ImgID` INT NOT NULL AUTO_INCREMENT,
  `Imgname` VARCHAR(100) NOT NULL,
  `Imgloc` VARCHAR(200) NOT NULL,
  `ObjImgloc` VARCHAR(200) NOT NULL,
  `Uploaded_time` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ImgID`),
  UNIQUE INDEX `ImgID_UNIQUE` (`ImgID` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `a1_db`.`user_has_imgs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `a1_db`.`user_has_imgs` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `userinfo_UserID` INT NOT NULL,
  `imgs_ImgID` INT NOT NULL,
  PRIMARY KEY (`ID`, `userinfo_UserID`, `imgs_ImgID`),
  INDEX `fk_user_has_imgs_userinfo_idx` (`userinfo_UserID` ASC),
  INDEX `fk_user_has_imgs_imgs1_idx` (`imgs_ImgID` ASC),
  UNIQUE INDEX `ID_UNIQUE` (`ID` ASC),
  CONSTRAINT `fk_user_has_imgs_userinfo`
    FOREIGN KEY (`userinfo_UserID`)
    REFERENCES `a1_db`.`userinfo` (`UserID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_has_imgs_imgs1`
    FOREIGN KEY (`imgs_ImgID`)
    REFERENCES `a1_db`.`imgs` (`ImgID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;


