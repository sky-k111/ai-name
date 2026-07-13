BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help dev backend frontend build clean db-status db-reset deps status

help:
	@echo "AI 智能取名系统 - 开发工作流"
	@echo ""
	@echo "开发命令:"
	@echo "  make dev        提示需要两个终端"
	@echo "  make backend    启动后端 :8000 (Swagger :8000/docs)"
	@echo "  make frontend   启动前端 :5173"
	@echo "  make deps       安装所有依赖"
	@echo ""
	@echo "构建和清理:"
	@echo "  make build      前端生产构建"
	@echo "  make clean      清理构建产物"
	@echo ""
	@echo "数据库 (MySQL Docker):"
	@echo "  make db-status  查看数据库状态和表"
	@echo "  make db-reset   清空测试数据（保留用户和管理员）"
	@echo ""
	@echo "其他:"
	@echo "  make status     查看 git 状态"

backend:
	@echo "启动后端开发服务器... 端口 8000"
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@echo "启动前端开发服务器... 端口 5173"
	cd $(FRONTEND_DIR) && npm run dev

dev:
	@echo "需要两个终端分别运行:"
	@echo "  终端1: make backend"
	@echo "  终端2: make frontend"

deps:
	@echo "安装后端依赖..."
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	@echo "安装前端依赖..."
	cd $(FRONTEND_DIR) && npm install

build:
	@echo "构建前端生产版本..."
	cd $(FRONTEND_DIR) && npm run build
	@echo "完成 -> $(FRONTEND_DIR)/dist/"

clean:
	@echo "清理构建产物..."
	cd $(FRONTEND_DIR) && rm -rf dist
	@echo "完成"

db-status:
	@echo "MySQL 容器状态:"
	@docker ps --filter name=mysql --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  未运行，启动: docker start mysql"
	@echo ""
	@echo "数据库表:"
	@docker exec mysql mysql -uroot -prootpassword naming_db -e "SHOW TABLES;" 2>/dev/null || echo "  无法连接数据库"

db-reset:
	@echo "清空测试数据（保留用户和管理员）..."
	@docker exec mysql mysql -uroot -prootpassword naming_db -e "DELETE FROM naming_history; DELETE FROM auth_logs; DELETE FROM email_verifications; DELETE FROM transactions; DELETE FROM daily_usage; DELETE FROM favorites;" 2>/dev/null
	@echo "测试数据已清空"

status:
	@git status
	@echo ""
	@echo "最近提交:"
	@git log --oneline -3
