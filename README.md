# 马原刷题

马克思主义基本原理在线刷题平台，539 题题库，支持背题、测试、错题本三种模式。

## 在线访问

👉 **[http://23.94.184.2:8080/](http://23.94.184.2:8080/)**

## 功能

- **📖 背题模式** — 顺序刷题，单选点击即判、多选提交查看答案，答错自动收入错题本
- **📝 测试模式** — 随机抽 100 题，交卷统一判分，查看详细答题报告
- **❌ 错题本** — 自动收录错题，支持重刷、逐条删除、清空（localStorage 持久化）

## 技术栈

- 后端：Python Flask + Gunicorn
- 前端：原生 HTML/CSS/JS，无框架依赖
- 部署：systemd 管理，开机自启

## 本地运行

```bash
cd webapp
pip install flask
python app.py
# 访问 http://localhost:8080
```

## 项目结构

```
.
├── webapp/
│   ├── app.py              # Flask 后端 API
│   ├── questions.json      # 题库数据（539 题）
│   └── templates/
│       └── index.html      # 前端单页应用
├── merge_questions.py      # 题库合并去重脚本
├── questions.json          # 题库（与 webapp 内同步）
└── 马克思主义基本原理题库_整合版.docx  # 排版好的 Word 题库
```

## License

MIT
