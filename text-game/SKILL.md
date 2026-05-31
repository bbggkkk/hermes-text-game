---
name: hermes-text-game
description: 텍스트 기반 인터랙티브 게임을 진행합니다. 스크립트로 게임 마스터 프롬프트를 생성하고, 에이전트가 직접 게임을 운영합니다.
version: 4.0.0
author: Hana
---

# Hermes Text Game Skill

에이전트가 **게임 마스터(GM)**가 되어 텍스트 게임을 직접 진행합니다.
스크립트([prompt.py](file:///home/hana/sources/@hermes/hermes-text-game/text-game/scripts/prompt.py))는 장르와 테마에 맞는 시스템 프롬프트만 생성하고, 게임 운영은 에이전트 자신이 수행합니다.

---

## 작동 방식

### 1. 게임 시작
사용자가 게임을 원하면 스크립트를 실행하여 프롬프트를 받습니다:

```bash
python3 text-game/scripts/prompt.py --genre "장르" --theme "테마"
```

반환된 JSON의 `"prompt"` 값을 읽고, 그 지시에 따라 게임을 시작합니다.

### 2. 게임 진행
에이전트가 프롬프트의 출력 형식을 지키며 직접 게임을 운영합니다.
사용자의 자연어 입력을 해석하여 스토리를 전개하고 상태를 추적합니다.
별도의 엔진 호출은 없습니다.
