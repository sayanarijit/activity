SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE `activity`;
USE `activity`;

CREATE TABLE `reports` (
  `id` int(200) UNSIGNED NOT NULL,
  `user` varchar(50) NOT NULL,
  `reportid` varchar(50) NOT NULL,
  `action` varchar(200) NOT NULL,
  `hostname` varchar(50) NOT NULL,
  `command` longtext NOT NULL,
  `stdout` longtext,
  `stderr` longtext,
  `exit_code` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `reports`
  MODIFY `id` int(200) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=0;
