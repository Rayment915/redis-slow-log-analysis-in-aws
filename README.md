# redis-slow-log-analysis-in-aws
# For detail user guide, please refer to https://aws.amazon.com/cn/blogs/china/build-elasticache-for-redis-slow-log-visualization-platform/

简介
Redis数据库是一个基于内存的 key-value存储系统，现在redis最常用的使用场景就是存储缓存用的数据，在需要高速读/写的场合使用它快速读/写，从而缓解应用数据库的压力，进而提升应用处理能力。许多数据库会提供慢查询日志帮助开发和运维人员定位系统存在的慢操作。所谓慢查询日志就是系统在命令执行前后计算每条命令的执行时间，当超过预设阀值，就将这条命令的相关信息（例如：发生时间，耗时，命令的详细信息）记录下来，Redis也提供了类似的功能。
 
本文将基于AWS托管的服务来介绍如何展示和分析大规模Redis 集群慢日志。
1.架构说明
通过Event Bridge 产生定时任务（1分钟）触发Lambda 执行，Lambda 通过aws 的sdk找到所有redis 的节点信息并一个个连接索取慢日志信息。 通过慢日志自带的时间戳过滤出最近1分钟产生的日志并上传到RDS数据库保存，最终通过托管的Grafana 展示并统计
https://s3.cn-north-1.amazonaws.com.cn/awschinablog/build-elasticache-for-redis-slow-log-visualization1.jpg

