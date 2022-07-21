# redis-slow-log-analysis-in-aws


Redis的慢日志会记录超过指定response time 的操作和key，这些日志对分析业务性能瓶颈十分有用。但是日志本身不会持久化，格式不友好，大规模部署了实例的情况下要集中式展示和分析比较困难，本代码将基于AWS 的elasticache 和相关云上的服务解决以上提到的痛点。

For detail user guide, please refer to https://aws.amazon.com/cn/blogs/china/build-elasticache-for-redis-slow-log-visualization-platform/

