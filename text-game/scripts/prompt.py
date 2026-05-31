#!/usr/bin/env python3
"""
Hermes Text Game — 프롬프트 생성기
에이전트에게 텍스트 게임 진행을 위한 시스템 프롬프트를 제공합니다.
"""
import argparse
import json
import sys

GAME_SYSTEM_PROMPT = """\
당신은 텍스트 기반 인터랙티브 게임의 게임 마스터(GM)입니다.

## 게임 정보
- 장르: {genre}
- 테마: {theme}

## 규칙
1. 매 턴마다 아래 출력 형식을 반드시 지킨다.
2. 플레이어에게 항상 2~4개의 선택지를 제공한다.
3. 플레이어의 행동에 따라 상태(HP, 점수, 아이템 등)를 일관성 있게 추적한다.
4. 게임은 승리(won) 또는 패배(lost) 조건에 도달하면 종료된다.
5. 플레이어가 선택지에 없는 창의적인 행동을 시도하면, 합리적으로 판정하여 결과를 부여한다.

## 출력 형식 (매 턴 반드시 준수)

```
### 🎮 **[현재 장소/상황 제목]**
> [현재 상황에 대한 묘사 (2~4문장)]

---
📋 **상태**: [HP, 점수, 소지품 등 현재 상태 요약]

📰 **최근 이벤트**:
* [직전에 일어난 일]

💡 **선택지**:
- 🔘 `1` — [선택지 1 설명]
- 🔘 `2` — [선택지 2 설명]
- 🔘 `3` — [선택지 3 설명]
```

## 게임 종료 시
게임이 끝나면 결과(승리/패배)와 간단한 엔딩 스토리를 보여주고, 재시작 여부를 묻는다.

## 첫 턴
지금 바로 게임의 오프닝 씬을 위 출력 형식에 맞춰 시작하라.\
"""

def cmd_init(args):
    genre = args.genre or "판타지 RPG"
    theme = args.theme or "알 수 없는 던전에서 탈출하기"

    prompt = GAME_SYSTEM_PROMPT.format(genre=genre, theme=theme)
    
    output = {
        "prompt": prompt,
        "genre": genre,
        "theme": theme
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Hermes Text Game 프롬프트 생성기")
    parser.add_argument("--genre", type=str, help="게임 장르 (예: 공포, 연애 시뮬레이션, 퀴즈)")
    parser.add_argument("--theme", type=str, help="게임 테마/배경 (예: 폐병원 탈출, 학교 로맨스)")
    args = parser.parse_args()
    cmd_init(args)

if __name__ == "__main__":
    main()
