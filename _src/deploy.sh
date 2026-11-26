#!/bin/bash
# 사용: ./deploy.sh "커밋 메시지"
set -e
cd /home/claude/site && git stash -q -u 2>/dev/null || true; git pull -q --rebase; git stash pop -q 2>/dev/null || true
python3 /home/claude/tempal/build_site.py /home/claude/site && python3 /home/claude/tempal/gen_og.py && python3 /home/claude/tempal/prerender.py /home/claude/site | tail -1
# 자동 점검: 실패하면 올리지 않는다
if ! python3 /home/claude/tempal/check_site.py /home/claude/site; then echo "배포 중단: 위 문제를 먼저 고치세요"; exit 1; fi
# 원본 소스도 저장소에 보관 (다음 작업 때 복구용, 페이지로 읽히지 않게 .txt)
mkdir -p /home/claude/site/_src && cp /home/claude/tempal/index.html /home/claude/site/_src/source_index.html.txt && cp /home/claude/tempal/{build_site.py,gen_og.py,prerender.py,check_site.py,deploy.sh} /home/claude/site/_src/
git add -A && git commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Acpr1h6BLddixputi4M4Kd" && git push -q && git log --oneline -1
