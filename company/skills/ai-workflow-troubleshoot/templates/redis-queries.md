# Redis 数据探查模板

通过 BeanShell 后门调用 `IStoreDao`。🔴 **仅限线下环境**，线上禁止执行。

## Bean 名称确认

首次使用时需确认 `${STORE_DAO_BEAN}`（IStoreDao 实现类的 Bean 名称）：

```bash
rg "implements.*IStoreDao|@Autowired.*IStoreDao|@Resource.*IStoreDao" --type java
```

## 查询模板

### 查询 String 类型

```java
String value = context.getBean("${STORE_DAO_BEAN}").get("${REDIS_KEY}");
value
```

### 查询 Hash 类型

```java
// 全部字段
java.util.Map result = context.getBean("${STORE_DAO_BEAN}").hgetAll("${REDIS_KEY}");
result

// 单个字段
String value = context.getBean("${STORE_DAO_BEAN}").hget("${REDIS_KEY}", "${FIELD}");
value
```

### 批量查询（Pipeline）

```java
java.util.ArrayList keys = new java.util.ArrayList();
keys.add("key1");
keys.add("key2");
java.util.List values = context.getBean("${STORE_DAO_BEAN}").mget(keys);
values
```

### 检查 Key 存在性 / TTL

```java
Boolean exists = context.getBean("${STORE_DAO_BEAN}").exists("${REDIS_KEY}");
exists

Long ttl = context.getBean("${STORE_DAO_BEAN}").ttl("${REDIS_KEY}");
ttl
```

### Set / List / Sorted Set

```java
// Set 成员
java.util.Set members = context.getBean("${STORE_DAO_BEAN}").smembers("${REDIS_KEY}");
members

// List 范围查询
java.util.List list = context.getBean("${STORE_DAO_BEAN}").lrange("${REDIS_KEY}", 0, -1);
list

// Sorted Set 范围查询（含分数）
java.util.Set zset = context.getBean("${STORE_DAO_BEAN}").zrangeWithScores("${REDIS_KEY}", 0, -1);
zset
```

## Redis Key 定位方法

1. 在代码中搜索 Key 模式：
   ```bash
   rg "Keys\." --type java -l
   rg "static.*class.*Keys" --type java
   ```

2. 从 DAO 层追溯：
   ```bash
   rg "storeDao\.(get|set|hget|hset)" --type java
   ```

3. 根据代码中的 Key 模板（通常含 uid/roomId 等变量）替换为实际值。

## 执行方式

```bash
PYBIN="$HOME/.cursor/skills-venv/bin/python"
SCRIPT="$HOME/.cursor/skills/generate-spring-bean-call/scripts/execute_with_mse.py"
$PYBIN $SCRIPT --code 'context.getBean("${STORE_DAO_BEAN}").get("${REDIS_KEY}")'
```
