---
name: hermes-text-game
description: 범용 텍스트 기반 상태 머신 게임 엔진을 구동합니다. RPG, 미연시, 퀴즈 서바이벌 등 다양한 장르의 설정을 동적으로 로드하고, 플레이어의 자연어 입력을 각 장르의 선택 명령어로 매핑해 실행하고 구조화된 화면을 출력합니다.
version: 2.0.0
author: Hana
---

# Hermes Universal Text Game Engine Skill

이 스킬은 **범용 텍스트 기반 상태 머신 게임 엔진**을 활용해 다양한 장르(RPG, 비주얼 노벨, 퀴즈 등)의 게임을 플레이할 수 있도록 해줍니다.
게임 로직과 세이브/설정 관리는 [game_engine.py](file:///home/hana/sources/@hermes/hermes-text-game/text-game/scripts/game_engine.py)를 사용합니다.

특히, 에이전트(Hermes)는 물리적인 설정 파일이나 세이브 파일을 디스크에 생성하지 않고, **에이전트 메모리에서 실시간으로 시나리오(Config JSON)와 이전 턴의 상태(State JSON)를 유지하며 호출하는 무상태(Stateless) 실시간 모드**로 작동할 수 있습니다.

## 1. 런타임 실시간 시나리오
모든 시나리오 설정(Config JSON)과 플레이 기록 상태(State JSON)는 파일로 저장되지 않으며, 에이전트(Hermes)가 런타임에 실시간으로 구상하고 이전 턴 결과를 메모리(Context)에 유지하며 백엔드 스크립트를 호출해 나갑니다.

---

## 2. 작동 방식 (Workflow)

디스크 I/O 없이 에이전트가 메모리 상에서 config와 state를 실시간으로 가공하고 주고받는 100% 무상태(Stateless) 구조입니다.

1.  **게임 초기화 (Init)**:
    에이전트는 플레이하고 싶은 룰셋(Config JSON 문자열)을 빌드하고, 초기 상태를 전달받기 위해 스크립트를 호출합니다 (`--config-data`는 필수입니다):
    ```bash
    python3 text-game/scripts/game_engine.py --init --config-data '<Config_JSON_문자열>' --state-data '{}'
    ```
    *   반환값인 JSON에서 `"game_state"` 객체(전체 게임 상태)를 에이전트가 기억(Context에 저장)합니다.

2.  **행동 진행 (Command)**:
    사용자가 대답을 남기면 적합한 커맨드로 정규화한 뒤, **기억하고 있던 직전 턴의 `game_state` 객체**와 **설정 JSON**을 각각 문자열 인자로 다시 주입합니다:
    ```bash
    python3 text-game/scripts/game_engine.py --command "<mapped_command>" --config-data '<Config_JSON_문자열>' --state-data '<직전_턴의_game_state_JSON_문자열>'
    ```
    *   스크립트는 수신한 상태와 설정을 토대로 연산한 뒤, 갱신된 새로운 게임 상태 `"game_state"`를 반환합니다. 에이전트는 이를 다음 턴을 위해 다시 기억합니다.

---

## 3. 엔진 출력 구조 (JSON Schema)

스크립트는 매 액션마다 아래의 범용 JSON 데이터를 반환합니다.

```json
{
  "success": true, // 명령어 처리 성공 여부
  "message": "처리에 따른 결과 또는 피드백 메시지",
  "game_over": false, // 게임 최종 오버/클리어 여부
  "ending": "playing", // playing, won (승리), lost (패배)
  "ui_display": {
    "room_title": "현재 장면/방의 렌더링된 제목",
    "room_description": "상태 변수가 치환된 현재 씬의 본문 묘사",
    "status_bar": "점수, 체력, 인벤토리 등 장르별 요약 상태 바",
    "available_actions": [
      "선택 가능한 행동 번호 및 텍스트 목록 (met=False인 조건은 비활성화 표시됨)"
    ],
    "logs": [
      "최근 게임 진행 이벤트 로그 (최대 3개)"
    ]
  },
  "game_state": {
    "current_scene": "현재 씬 ID",
    "status": "게임 진행 상태",
    "variables": {
      "변수명": "현재 상태 변수값 (HP, Score, Love, Inventory 등)"
    }
  }
}
```

---

## 4. 사용자 응답 템플릿 (Response Formatting)

에이전트는 아래의 고급 테마 마크다운 형식을 사용하여 플레이어에게 상태를 전달합니다.

```markdown
### 🎮 **[ui_display.room_title]**
> [ui_display.room_description]

---

📋 **상태 정보**: `[ui_display.status_bar]`

📰 **최근 이벤트**:
[logs에 있는 로그들을 리스트로 출력]
* *[이벤트 메시지]*

💡 **선택 가능한 행동**:
[available_actions에 표시된 명령들을 목록으로 제공]
- 🔘 `1` (인사하기)
- 🔘 `2` (피하기)
```

만약 사용자가 디버깅을 위해 생데이터를 원할 경우, `game_state` 딕셔너리 정보 또는 스크립트가 반환한 JSON 원본을 마크다운 코드 블록으로 그대로 노출해 줍니다.
