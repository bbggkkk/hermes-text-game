#!/usr/bin/env python3
import json
import sys
import argparse

def format_for_discord(data):
    title = data.get("title", "제목 없음")
    description = data.get("description", "묘사가 없습니다.")
    status = data.get("status", {})
    events = data.get("events", [])
    choices = data.get("choices", [])
    game_over = data.get("game_over", False)
    
    lines = []
    
    # 1. 제목 및 상황 묘사
    lines.append(f"## ❖ **{title}** ❖")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Discord에서 blockquote 렌더링을 위해 각 줄에 > 를 붙임
    desc_lines = description.split('\n')
    for dl in desc_lines:
        if dl.strip():
            lines.append(f"> {dl.strip()}")
    lines.append("")
    
    # 2. 상태창 (코드 블록을 사용하여 깔끔하게 정렬)
    lines.append("▤ **현재 상태**")
    lines.append("```yaml")
    if isinstance(status, dict) and status:
        for k, v in status.items():
            lines.append(f"{k}: {v}")
    elif isinstance(status, str) and status:
        lines.append(status)
    else:
        lines.append("상태 이상 없음")
    lines.append("```")
    lines.append("")
    
    # 3. 최근 이벤트
    if events:
        lines.append("◈ **최근 이벤트**")
        for event in events:
            lines.append(f"  - {event}")
        lines.append("")
        
    # 4. 선택지
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if game_over:
        lines.append("🛑 **게임 종료**")
        lines.append("> 플레이해주셔서 감사합니다. 재시작하려면 말씀해 주세요.")
    else:
        lines.append("💡 **무엇을 할까요?** `(번호나 텍스트로 입력)`")
        for choice in choices:
            key = choice.get("key", "")
            text = choice.get("text", "")
            lines.append(f"  ▷ `[{key}]` {text}")
            
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="디스코드 전용 텍스트 게임 렌더링 엔진")
    parser.add_argument("--data", type=str, required=True, help="장면 데이터를 담은 JSON 문자열")
    args = parser.parse_args()
    
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"❌ [Error] 유효한 JSON 문자열이 아닙니다: {e}")
        sys.exit(1)
        
    print(format_for_discord(data))

if __name__ == "__main__":
    main()
