# Engineering Discipline

## 1. 总则

工程质量主要前置到 contract / plan / spec，而不是依赖流程末尾的人工技术审查。

## 2. 门禁

- 没有 contract，不进入正式需求开发。
- standard / large 没有 confirmed plan，不进入 implement。
- 没有 test 验证结果，不进入 approve。
- test 未通过，不进入 approve。
- test 未审批通过，不进入知识沉淀。

## 3. 规范入口

- Ritual 阶段只读 `.ruyi/INDEX.md`。
- 需要项目规范时，先读 `.ruyi/spec/INDEX.md`。
- INDEX 不存在时，只扫描 `.ruyi/contracts/`、`.ruyi/plans/`、`.ruyi/tests/` 的目录名，不读文件正文。

## 4. 代码质量结论

实现阶段产生的可复用质量结论，应进入 test、spec candidate 或正式 spec。不要只留在本地 task。
