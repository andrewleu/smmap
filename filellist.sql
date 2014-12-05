CREATE TABLE `filelist` (
  `id` bigint(8) NOT NULL AUTO_INCREMENT,
  `server` varchar(64) NOT NULL DEFAULT '',
  `name` varchar(128) DEFAULT NULL,
  `filename` varchar(128) NOT NULL DEFAULT '',
  `mediatype` varchar(64) DEFAULT NULL,
  `rand` varchar(10) DEFAULT NULL,
  `encryptstr` varchar(128) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`server`,`filename`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `encrpt` (`encryptstr`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


