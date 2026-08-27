# 任务目录说明

任务产物存放在业务项目内：`{project}/.docs/PROCESS/{YYYYMMDD}-{slug}/`，内含 state.md 与各阶段产物。

本目录（`runtime/tasks/`）仅存放全局调度状态：

- `CURRENT` 文件：存放当前活跃任务的完整路径（格式：`{project_path}/.docs/PROCESS/{task_dir}`），无活跃任务时为空。由 ai-workflow-dev / ai-workflow-bugfix 自动维护。

任务产物与工作流引擎文件的区分见 `docs/PROMPTS-SUPPLEMENT.md` [S1]。
