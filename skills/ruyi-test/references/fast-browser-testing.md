# Fast-Browser Testing

## 1. 定位

Ruyi 在 `ruyi-test` 阶段对接已有 fast-browser CLI，用于 UI 自动化验证、失败诊断和可复用测试资产沉淀。

contract 中的测试用例可以是自然语言；本阶段负责把它转成可执行验证路径和证据。

本参考内化自本地 `fast-browser-agent` skill 的使用方式，但 Ruyi 不依赖该 skill 运行。Ruyi 只要求 test 阶段优先尝试 fast-browser CLI，并把执行证据写入正式 test 产物。

## 2. 优先级

优先使用最高可复用层级：

1. `fast-browser case run`
2. `fast-browser flow run`
3. `fast-browser site <adapter>/<command>`
4. 低层浏览器命令

console、network、screenshot、trace 属于失败诊断层，不是默认展示路径。

## 3. 最小预检

```bash
fast-browser health
fast-browser workspace --json
fast-browser browser status --json
fast-browser list
```

如果已有目标站点能力，还应检查：

```bash
fast-browser info <site> --json
fast-browser info <site>/<command> --json
```

## 4. 规则

- 不猜测是否需要登录、是否允许 headed、是否要稳定 session。
- UI 自动化失败时，记录失败证据，不粉饰为通过。
- 成功路径如果后续会复用，应建议沉淀为 case、flow 或 site 能力。
- formal test 文件记录结论和证据，不保存临时 selector、tabId 或 raw snapshot。
