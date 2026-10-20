# ES 业务数据查询模板

通过 BeanShell 后门调用 ES 客户端。🔴 **仅限线下环境**，线上禁止执行。

## Bean 名称确认

首次使用时需确认：

| 配置项 | 说明 | 确认方式 |
|--------|------|---------|
| `${ES_CLIENT_BEAN}` | ES 客户端 Bean 名称 | `rg "RestHighLevelClient\|ElasticsearchClient\|@Bean.*elastic" --type java` |
| `${ES_QUERY_BEAN}` | 业务 ES 查询服务 Bean | 搜索业务封装的 ES 查询类 |

## 查询模板

### 通过业务服务查询（推荐）

```java
// 优先使用业务层已封装的查询方法
Object result = context.getBean("${ES_QUERY_BEAN}").${queryMethod}("${PARAM}");
result
```

### 通过 RestHighLevelClient 直接查询

```java
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.builder.SearchSourceBuilder;

SearchRequest request = new SearchRequest("${INDEX_NAME}");
SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
sourceBuilder.query(QueryBuilders.termQuery("${FIELD}", "${VALUE}"));
sourceBuilder.size(10);
request.source(sourceBuilder);

SearchResponse response = context.getBean("${ES_CLIENT_BEAN}").search(request);
response.getHits().getTotalHits().value + " hits, first: " + response.getHits().getHits()[0].getSourceAsString()
```

## ES 索引定位方法

```bash
rg "IndexName|indexName|INDEX" --type java -l
rg "@Document|@Setting" --type java
rg "SearchRequest|ElasticsearchTemplate|RestHighLevelClient" --type java -l
```

## 执行方式

```bash
PYBIN="$HOME/.cursor/skills-venv/bin/python"
SCRIPT="$HOME/.cursor/skills/generate-spring-bean-call/scripts/execute_with_mse.py"
$PYBIN $SCRIPT --code '生成的 ES 查询代码'
```
