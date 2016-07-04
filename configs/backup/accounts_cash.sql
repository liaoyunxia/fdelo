CREATE TABLE `accounts_cash` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `available_balance` bigint(20) NOT NULL DEFAULT '0',
  `withdraw_frozen_balance` bigint(20) NOT NULL DEFAULT '0' COMMENT '取现冻结资金，单位分',
  `invest_frozen_balance` bigint(20) NOT NULL DEFAULT '0' COMMENT '投资冻结资金，单位分',
  `status` smallint(5) unsigned NOT NULL,
  `created_time` datetime(6) NOT NULL,
  `updated_time` datetime(6) NOT NULL,
  `payment_service_id` int(11) NOT NULL,
  `interest` bigint(20) NOT NULL DEFAULT '0' COMMENT '待获收益，单位分',
  `principal` bigint(20) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
