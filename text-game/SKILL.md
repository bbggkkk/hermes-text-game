---
name: hermes-text-game
description: 범용 텍스트 기반 상태 머신 게임 엔진. 에이전트가 사용자의 요청에 따라 실시간으로 게임 시나리오(Config JSON)를 창작하고, 엔진 스크립트를 호출하여 상태를 전이시키며, 구조화된 출력을 렌더링한다. 모든 장르를 지원한다.
version: 3.0.0
author: Hana
---

# Hermes Universal Text Game Engine Skill

에이전트가 사용자의 요청에 따라 **게임 시나리오를 실시간으로 창작**하고, 상태 머신 엔진 스크립트([game_engine.py](file:///home/hana/sources/@hermes/hermes-text-game/text-game/scripts/game_engine.py))를 호출하여 게임을 진행합니다.

**핵심 원칙**: 사전에 준비된 시나리오 파일은 존재하지 않습니다. 에이전트가 사용자와의 대화를 통해 어떤 게임을 하고 싶은지 파악한 뒤, 직접 Config JSON을 설계하여 엔진에 주입합니다.

---

## 1. 작동 방식 (Workflow)

### Step 1: 사용자의 요청 파악
사용자가 "게임 하자", "퀴즈 하고 싶어", "공포 탈출 게임 만들어줘" 등을 말하면, 에이전트는 장르·테마·난이도 등을 자유롭게 대화로 결정합니다.

### Step 2: Config JSON 실시간 설계
에이전트는 아래 Config JSON Schema에 맞춰 게임 시나리오를 직접 창작합니다. 이 JSON은 파일로 저장하지 않고 메모리에만 보관합니다.

### Step 3: 엔진 초기화
설계한 Config JSON을 엔진에 주입하여 초기 상태를 받습니다:
```bash
python3 text-game/scripts/game_engine.py --init \
  --config-data '<에이전트가_창작한_Config_JSON>' \
  --state-data '{}'
```
반환된 `"game_state"` 객체를 에이전트가 컨텍스트에 기억합니다.

### Step 4: 매 턴 진행
사용자의 자연어 입력을 `available_actions`에 매핑한 뒤:
```bash
python3 text-game/scripts/game_engine.py \
  --command "<매핑된_명령어>" \
  --config-data '<동일한_Config_JSON>' \
  --state-data '<직전_턴의_game_state_JSON>'
```
반환된 새 `"game_state"`를 다시 기억하고, `"ui_display"`를 렌더링합니다.

---

## 2. Config JSON Schema (에이전트가 창작해야 하는 구조)

```json
{
  "engine_settings": {
    "start_scene": "첫 씬의 ID",
    "start_log": "게임 시작 시 표시할 첫 로그 메시지",
    "status_bar_template": "상태바 템플릿. 변수는 {변수명} 형태로 삽입"
  },
  "initial_state": {
    "variables": {
      "변수명": "초기값 (숫자, 문자열, 배열 모두 가능)"
    }
  },
  "scenes": {
    "씬ID": {
      "title": "씬 제목 ({변수명} 치환 가능)",
      "description": "씬 본문 묘사 ({변수명} 치환 가능)",
      "auto_rules": [
        {
          "conditions": [{"variable": "변수명", "operator": "<=", "value": 0}],
          "game_over": true,
          "ending": "won 또는 lost",
          "message": "자동 트리거 시 표시 메시지"
        }
      ],
      "choices": [
        {
          "input": "사용자가 입력할 명령어 (번호 또는 텍스트)",
          "text": "선택지 설명 텍스트",
          "conditions": [
            {
              "variable": "변수명",
              "operator": "== | != | > | >= | < | <= | contains | not_contains",
              "value": "비교 대상 값",
              "fail_message": "조건 미충족 시 안내 메시지"
            }
          ],
          "effects": [
            {
              "variable": "변수명",
              "operator": "= | + | - | append | remove",
              "value": "적용할 값"
            }
          ],
          "next_scene": "이동할 씬 ID (생략 시 현재 씬 유지)",
          "message": "선택 시 표시할 결과 메시지 ({변수명} 치환 가능)",
          "game_over": false,
          "ending": "won 또는 lost (game_over가 true일 때만 적용)"
        }
      ]
    }
  }
}
```

### 연산자 레퍼런스
| 카테고리 | 연산자 | 설명 |
|---|---|---|
| 조건(conditions) | `==`, `!=`, `>`, `>=`, `<`, `<=` | 숫자/문자열 비교 |
| 조건(conditions) | `contains`, `not_contains` | 배열에 값 포함 여부 |
| 효과(effects) | `=` | 값 대입 |
| 효과(effects) | `+`, `-` | 숫자 덧셈/뺄셈 |
| 효과(effects) | `append`, `remove` | 배열에 항목 추가/제거 |

---

## 3. 엔진 출력 구조 (JSON)

엔진은 매 호출마다 아래 JSON을 STDOUT으로 반환합니다:

```json
{
  "success": true,
  "message": "결과 메시지",
  "game_over": false,
  "ending": "playing | won | lost",
  "ui_display": {
    "room_title": "렌더링된 씬 제목",
    "room_description": "변수 치환된 씬 본문",
    "status_bar": "변수 치환된 상태바",
    "available_actions": ["선택 가능한 행동 목록"],
    "logs": ["최근 이벤트 로그 (최대 3개)"]
  },
  "game_state": { "...다음 턴에 --state-data로 전달할 전체 상태..." }
}
```

---

## 4. 사용자 응답 렌더링 템플릿

`ui_display` 데이터를 아래 형식으로 변환하여 출력합니다:

```markdown
### 🎮 **[room_title]**
> [room_description]

---
📋 **상태**: `[status_bar]`

📰 **최근 이벤트**:
* [각 로그 항목]

💡 **행동 선택**:
- 🔘 `[input]` — [text]
```

---

## 5. 에이전트 행동 규칙

1. **시나리오를 파일로 저장하지 않는다.** 모든 Config JSON은 에이전트의 컨텍스트 메모리에서만 유지한다.
2. **사용자의 자연어를 `available_actions`의 input 값으로 매핑한다.** 정확히 일치하지 않아도 의도가 분명하면 가장 가까운 선택지로 매핑한다.
3. **game_state는 매 턴 반환값에서 갱신하여 기억한다.** 에이전트가 임의로 game_state를 조작하지 않는다.
4. **게임이 끝나면(`game_over: true`) 결과를 안내하고, 재시작 여부를 묻는다.**
