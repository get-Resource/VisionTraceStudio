

# 目录结构
VisionTraceStudio/ 
│
├── app/                    # 应用程序代码
│   ├── api/           # 后端API
│   ├── core/           # 核心代码
│   ├── db/           # 前端代码
│   │   ├── crud/            # 数据库四种基本操作
│   │   └── models/         # 数据库模型
│   │   └── schemas/         # 交互数据结构模型
│   │
│   ├── backend/            # 后端代码
│   │   ├── src/            # 后端源代码
│   │   └── tests/          # 单元测试
│   │
│   └── Dockerfile          # 构建前后端镜像的Dockerfile
│
├── db/                     # 数据库相关文件
│   ├── migrations/         # 数据库迁移文件
│   └── init.sql            # 数据库初始化脚本
│
├── docs/                   # 文档目录
│   ├── design/             # 设计文档
│   ├── api/                # API文档
│   └── user_manual/        # 用户手册
│
├── .env                    # 环境变量文件
├── docker-compose.yml      # Docker Compose配置文件
├── requirements.txt        # Python依赖包列表
└── README.md               # 项目说明文档
