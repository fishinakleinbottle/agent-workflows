PROFILE ?= default

generate:
	python scripts/generate.py --profile $(PROFILE)

deploy-claude:
	@test -n "$(TARGET)" || (echo "TARGET required" && exit 1)
	mkdir -p $(TARGET)/.claude/skills $(TARGET)/.claude/agents
	cp -r dist/claude/skills/* $(TARGET)/.claude/skills/
	test -d dist/claude/agents && cp dist/claude/agents/* $(TARGET)/.claude/agents/ || true

deploy-cursor:
	@test -n "$(TARGET)" || (echo "TARGET required" && exit 1)
	mkdir -p $(TARGET)/.cursor/skills $(TARGET)/.cursor/rules
	cp -r dist/cursor/skills/* $(TARGET)/.cursor/skills/
	test -d dist/cursor/rules && cp dist/cursor/rules/* $(TARGET)/.cursor/rules/ || true

deploy-copilot:
	@test -n "$(TARGET)" || (echo "TARGET required" && exit 1)
	mkdir -p $(TARGET)/.copilot/skills
	cp -r dist/copilot/skills/* $(TARGET)/.copilot/skills/
	test -d dist/copilot/instructions && mkdir -p $(TARGET)/.github/instructions && \
		cp dist/copilot/instructions/* $(TARGET)/.github/instructions/ || true

sync:
	make generate PROFILE=$(PROFILE)
	make deploy-claude deploy-cursor deploy-copilot TARGET=$(TARGET)

diff:
	@echo "=== Claude ===" && diff -r dist/claude $(TARGET)/.claude 2>/dev/null || true
	@echo "=== Cursor ===" && diff -r dist/cursor/skills $(TARGET)/.cursor/skills 2>/dev/null || true
	@echo "=== Copilot ===" && diff -r dist/copilot/skills $(TARGET)/.copilot/skills 2>/dev/null || true

sync-all:
	@for p in $$(cat projects.txt); do echo "--- $$p ---" && make sync TARGET=$$p; done
