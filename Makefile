BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help dev backend frontend build clean status

help:
	@echo "开发常用命令："
	@echo "  make dev           - 本地开发（启动后端和前端）"
	@echo "  make backend       - 只启动后端开发服务"
	@echo "  make frontend      - 只启动前端开发服务器"
	@echo "  make build         - 构建生产版本"
	@echo "  make clean         - 清理临时文件和构建产物"
	@echo "  make status        - 检查 git 状态"

backend:
	@echo "启动后端开发服务..."
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "启动前端开发服务器..."
	@cd $(FRONTEND_DIR) && npm run dev

dev:
	@echo "启动完整开发环境..."
	@echo "先启动后端（在单独终端中运行 make backend）"
	@echo "再启动前端（在另一个终端中运行 make frontend）"
	@echo "或者启动两个后端进程："
	@-clear
	@printf "后端已在后台启动。端口 8000 用于 Swagger 调试。\n"
	@printf "前端已在后台启动。端口 5173 用于正常使用。\n"
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
	@cd $(FRONTEND_DIR) && npm run dev &
	@wait

build:
	@echo "构建生产版本..."
	@cd $(FRONTEND_DIR) && npm run build
	@echo "已生成 $(FRONTEND_DIR)/dist/"

clean:
	@echo "清理构建产物和临时文件..."
	@cd $(FRONTEND_DIR) && rm -rf node_modules dist
	@rm -f backend/naming.db
	@rm -f backend/naming.db-shm backend/naming.db-wal
	@rm -rf .pytest_cache
	@rm -rf frontend/node_modules

status:
	@git status
	@echo "\n最近一次提交："
	@git log --oneline -1
