CREATE TABLE `cards_card` (
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `user_image_urls` varchar(2000) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `id` bigint(20) NOT NULL,
  `caption` varchar(200) NOT NULL,
  `type` varchar(1) NOT NULL,
  `image_urls` varchar(2000) NOT NULL,
  `url` varchar(200) NOT NULL,
  `like_count` int(10) unsigned NOT NULL,
  `comment_count` int(10) unsigned NOT NULL,
  `tags` varchar(200) NOT NULL,
  `object_id` int(11) NOT NULL,
  `stream` varchar(200) NOT NULL,
  `player` varchar(200) NOT NULL,
  `site` varchar(12) NOT NULL,
  `tips` varchar(30) NOT NULL,
  `repost_count` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `cards_comment` (
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `user_image_urls` varchar(2000) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `id` bigint(20) NOT NULL,
  `is_origin` tinyint(1) NOT NULL,
  `card_id` bigint(20) NOT NULL,
  `text` varchar(200) NOT NULL,
  `like_count` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `cards_like` (
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `user_image_urls` varchar(2000) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `id` bigint(20) NOT NULL,
  `is_origin` tinyint(1) NOT NULL,
  `card_id` bigint(20) NOT NULL,
  `card_image_urls` varchar(2000) NOT NULL,
  `card_caption` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cards_like_user_id_6c5ef5f1_uniq` (`user_id`,`card_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `questions_vote` (
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(30) NOT NULL,
  `user_image_urls` varchar(2000) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `id` bigint(20) NOT NULL,
  `answer_id` int(11) NOT NULL,
  `type` varchar(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `questions_vote_user_id_d7cb3052_uniq` (`user_id`,`answer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
