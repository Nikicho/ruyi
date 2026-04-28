# Explain Schema

## 1. 对象定位

`explain` 是某次需求交付结果的开发简报，面向 PM 审批前阅读。

它不是审批结果本身，也不是代码 diff 摘要，也不替代 implement 阶段的 code review。

## 2. 路径规则

路径格式：

```text
explain/<module>/<feature>/<contract-date>.md
```

## 3. 头部元信息

建议包含：

- 审批状态
- 对应 Contract
- 对应 Plan
- 对应 Test

审批状态可以在审批动作之后更新。

## 4. 正文结构

```md
# Explain：[功能名称]

## 本次完成内容
## 与需求对照
## 验证结果
## 代码质量简报
## 代码质量来源
## 风险与遗留问题
## 技术备注
```

## 5. 技术备注规则

允许说明文件架构、hooks 拆分、组件设计、代码设计、关键技术取舍、自检/优化结论，以及少量高价值技术信息，例如技术债务、架构演进、兼容性限制。

不应写成大量代码变更清单、逐文件 diff 或实现过程流水账。

## 6. 硬门禁

- 没有需求定义锚点，不生成 explain。
- 没有 plan，不生成 explain。
- 没有 `test` 验证结果，不进入 explain 正式产出。
- test 结果为 `failed` 时，不进入 explain 正式产出。
- 代码质量简报必须显式写出来源，至少指向 plan、task 自检、review 结论或实际代码事实之一。
- explain 不能整体升级为 `spec`，只能作为提炼来源。
- 审批结论只能由 approve 阶段写入。
