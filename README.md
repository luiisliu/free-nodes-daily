# free-nodes-daily

每天自动抓取公开免费节点订阅，去重并做 TCP 连通性检查，生成可用的订阅文件。

> 免费公开节点非常不稳定，随时可能失效，仅供学习测试使用，不要用于银行、支付等敏感操作。

## 订阅地址（仓库创建后生效）

V2Ray / 通用订阅（base64）：

```
https://raw.githubusercontent.com/luiisliu/free-nodes-daily/main/sub.txt
```

原始节点列表：

```
https://raw.githubusercontent.com/luiisliu/free-nodes-daily/main/nodes.txt
```

## 更新方式

GitHub Actions 每天 UTC 00:00 自动运行 `fetch_nodes.py`，并把结果提交回本仓库。
也可以在仓库 Actions 页面手动点 Run workflow 立即更新一次。

## 文件说明

- `nodes.txt`：去重并 TCP 检查通过的节点链接
- `sub.txt`：`nodes.txt` 的 base64 订阅版
- `stats.json`：本次抓取数量和有效数量
- `fetch_nodes.py`：抓取脚本，来源均为公开免费订阅
