CREATE TABLE `cards` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL,
  `type` varchar(250) DEFAULT NULL,
  `publisher` varchar(20) DEFAULT NULL,
  `year` varchar(250) NOT NULL,
  `card_number` varchar(250) NOT NULL,
  `average_price` decimal(10,2) DEFAULT NULL,
  `max_price` decimal(10,2) DEFAULT NULL,
  `min_price` decimal(10,2) DEFAULT NULL,
  `url` varchar(250) DEFAULT NULL,
  `details` varchar(250) NOT NULL,
  `box_location` varchar(250) NOT NULL,
  `meta_data` json DEFAULT NULL,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6100 DEFAULT CHARSET=utf8;