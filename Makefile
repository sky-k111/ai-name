BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help dev backend frontend build clean status test db dev-deps ui-deps

help:
	@echo "AI 智能取名系统 - 开发工作流"
	@echo
	@echo "后端命令："
	@echo "  make backend   - 启动后端开发服务器 (端口 8000)"
	@echo "  make test       - 运行后端测试"
	@echo
	@echo "前端命令："
	@echo "  make frontend  - 启动前端开发服务器 (端口 5173)"
	@echo "  make build      - 构建生产版本"
	@echo
	@echo "开发快捷方式："
	@echo "  make dev        - 启动完整开发环境"
	@echo "  make deps       - 安装所有依赖"
	@echo
	@echo "维护命令："
	@echo "  make clean      - 清理临时文件和构建产物"
	@echo "  make status     - 检查 git 状态和日志"
	@echo "  make docs       - 打开主要文档"

backend:
	@echo "启动后端开发服务器... 端口 8000 (Swagger: http://localhost:8000/docs)"
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "启动前端开发服务器... 端口 5173 (应用: http://localhost:5173)"
	@cd $(FRONTEND_DIR) && npm run dev

dev: backend &
	delay = $$(
		printf "已在后台启动后端 (端口 8000)。\n"
		printf "前端将在5秒钟后启动...\n"
		sleep 5
		printf "已启动前端 (端口 5173)。\n"
		printf "提示：使用 'make frontend' 在单独终端中启动前端。\n"
	)
	@cd $(FRONTEND_DIR) && npm run dev

build:
	@echo "构建前端生产版本..."
	@cd $(FRONTEND_DIR) && npm run build
	@echo "已生成 $(FRONTEND_DIR)/dist/"

dev-deps:
	@echo "安装开发依赖..."
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@cd $(FRONTEND_DIR) && npm install

clean:
	@echo "清理构建产物和临时文件..."
	@cd $(BACKEND_DIR) && rm -f naming.db naming.db-shm naming.db-wal
	@cd $(FRONTEND_DIR) && rm -rf node_modules dist
	@rm -f backend/naming.db backend/naming.db-shm backend/naming.db-wal
	@rm -rf .pytest_cache

db:
	@echo "数据库管理..."
	@echo "1. 列出表：sqlite3 $(BACKEND_DIR)/naming.db '.tables'"
	@echo "2. 清空测试数据：sqlite3 $(BACKEND_DIR)/naming.db 'DELETE FROM naming_history; DELETE FROM user_logs; VACUUM;'"
	@echo "3. 重启服务：make backend"

status:
	@git status
	@echo "\n最近一次提交："
	@git log --oneline -1

