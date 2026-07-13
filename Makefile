BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help dev backend frontend build clean db-status db-reset deps status

help:
	@echo "AI 取名系统 - 开发工作流"
	@echo "  make backend    启动后端 :8000 (Swagger :8000/docs)"
	@echo "  make frontend   启动前端 :5173"
	@echo "  make deps       安装所有依赖"
	@echo "  make build      前端生产构建"
	@echo "  make clean      清理构建产物"
	@echo "  make db-status  查看 MySQL 状态和表"
	@echo "  make db-reset   清空测试数据"
	@echo "  make status     查看 git 状态"

backend:
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd $(FRONTEND_DIR) && npm run dev

deps:
	cd $(BACKEND_DIR) && pip install -r requirements.txt
	cd $(FRONTEND_DIR) && npm install

build:
	cd $(FRONTEND_DIR) && npm run build

clean:
	cd $(FRONTEND_DIR) && rm -rf dist

db-status:
	@docker ps --filter name=mysql --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo MySQL not running
	@docker exec mysql mysql -uroot -prootpassword naming_db -e "SHOW TABLES;" 2>/dev/null || echo Cannot connect

db-reset:
	@docker exec mysql mysql -uroot -prootpassword naming_db -e "DELETE FROM naming_history; DELETE FROM auth_logs; DELETE FROM email_verifications; DELETE FROM transactions; DELETE FROM daily_usage; DELETE FROM favorites;" 2>/dev/null
	@echo Done

status:
	@git status
	@git log --oneline -3
