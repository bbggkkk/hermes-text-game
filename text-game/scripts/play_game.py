import subprocess
import json
import sys

# 메모리 상에서 관리되는 장르별 기획 설정 데이터
# (디스크의 파일 입출력을 전혀 사용하지 않고 실행 시 전달용)
RPG_CONFIG = {
  "engine_settings": {
    "game_title": "던전 탐험 RPG",
    "start_scene": "start_room",
    "start_log": "게임이 시작되었습니다. 어두운 방에서 눈을 떴습니다.",
    "status_bar_template": "체력(HP): {hp}/{max_hp} | 무기: {equipped_weapon} | 인벤토리: {inventory}"
  },
  "initial_state": {
    "variables": {
      "hp": 100,
      "max_hp": 100,
      "equipped_weapon": "맨손",
      "has_rusty_key": True,
      "has_sword": True,
      "inventory": [],
      "monster_hp": 50
    }
  },
  "scenes": {
    "start_room": {
      "title": "낡은 침실 (Old Bedroom)",
      "description": "오래되어 먼지가 쌓인 침실입니다. 구석에 낡은 침대가 있고, 벽면에는 나무 서랍장이 놓여 있습니다. 동쪽(east)에는 먼지가 가득한 복도로 통하는 낡은 나무 문이 있습니다.",
      "choices": [
        {
          "input": "take rusty_key",
          "text": "바닥의 녹슨 열쇠를 줍는다",
          "conditions": [
            {
              "variable": "has_rusty_key",
              "operator": "==",
              "value": True,
              "fail_message": "바닥에 열쇠가 더 이상 없습니다."
            }
          ],
          "effects": [
            {
              "variable": "has_rusty_key",
              "operator": "=",
              "value": False
            },
            {
              "variable": "inventory",
              "operator": "append",
              "value": "녹슨 열쇠 (Rusty Key)"
            }
          ],
          "message": "녹슨 열쇠 (Rusty Key)을(를) 획득했습니다."
        },
        {
          "input": "move east",
          "text": "동쪽 복도로 이동한다",
          "next_scene": "hallway",
          "message": "어두운 복도로 걸어갔습니다."
        }
      ]
    },
    "hallway": {
      "title": "어두운 복도 (Dark Hallway)",
      "description": "길게 뻗은 어두운 복도입니다. 횃불이 벽에서 깜빡이고 있습니다. 서쪽(west)은 당신이 시작한 침실이고, 남쪽(south)에는 무기고의 철문이 보입니다. 동쪽(east)에는 거대한 해골 조각이 새겨진 철문이 있습니다.",
      "choices": [
        {
          "input": "move west",
          "text": "서쪽 침실로 돌아간다",
          "next_scene": "start_room",
          "message": "낡은 침실로 돌아갑니다."
        },
        {
          "input": "move south",
          "text": "남쪽 무기고로 들어간다",
          "next_scene": "armory",
          "message": "철문을 열고 무기고로 들어섭니다."
        },
        {
          "input": "move east",
          "text": "동쪽 해골 철문을 연다",
          "conditions": [
            {
              "variable": "inventory",
              "operator": "contains",
              "value": "녹슨 열쇠 (Rusty Key)",
              "fail_message": "거대한 해골 철문이 굳게 잠겨 있어 열리지 않습니다. 열쇠가 필요해 보입니다."
            }
          ],
          "effects": [
            {
              "variable": "inventory",
              "operator": "remove",
              "value": "녹슨 열쇠 (Rusty Key)"
            }
          ],
          "next_scene": "boss_room",
          "message": "녹슨 열쇠를 꽂아 돌리자 둔탁한 소리와 함께 해골 문이 열립니다!"
        }
      ]
    },
    "armory": {
      "title": "낡은 무기고 (Old Armory)",
      "description": "부서진 갑옷과 쓸모없는 무기 잔해들이 널려 있는 무기고입니다. 바닥을 자세히 보니 녹슬지 않은 튼튼한 강철 검이 놓여 있습니다. 북쪽(north)으로 나가면 복도로 돌아갑니다.",
      "choices": [
        {
          "input": "take sword",
          "text": "강철 검을 획득한다",
          "conditions": [
            {
              "variable": "has_sword",
              "operator": "==",
              "value": True,
              "fail_message": "이미 검을 주웠습니다."
            }
          ],
          "effects": [
            {
              "variable": "has_sword",
              "operator": "=",
              "value": False
            },
            {
              "variable": "inventory",
              "operator": "append",
              "value": "강철 검 (Steel Sword)"
            },
            {
              "variable": "equipped_weapon",
              "operator": "=",
              "value": "강철 검 (Steel Sword)"
            }
          ],
          "message": "강철 검 (Steel Sword)을(를) 획득했습니다. [무기 강철 검을 장착했습니다!]"
        },
        {
          "input": "move north",
          "text": "북쪽 복도로 돌아간다",
          "next_scene": "hallway",
          "message": "복도로 발걸음을 옮깁니다."
        }
      ]
    },
    "boss_room": {
      "title": "보스의 방 (Boss Room)",
      "description": "거대하고 음산한 방입니다. 방 한가운데 붉은 눈을 번뜩이는 고블린 전사(HP: {monster_hp})가 몽둥이를 들고 서 있습니다. 탈출을 위해서는 이 고블린을 쓰러뜨려야 합니다!",
      "auto_rules": [
        {
          "conditions": [
            {
              "variable": "monster_hp",
              "operator": "<=",
              "value": 0
            }
          ],
          "game_over": True,
          "ending": "won",
          "message": "고블린 전사가 비명을 지르며 쓰러졌습니다! 당신은 던전을 탈출하는 데 성공하여 승리했습니다!"
        },
        {
          "conditions": [
            {
              "variable": "hp",
              "operator": "<=",
              "value": 0
            }
          ],
          "game_over": True,
          "ending": "lost",
          "message": "체력이 0이 되었습니다... 눈앞이 캄캄해집니다. 게임 오버!"
        }
      ],
      "choices": [
        {
          "input": "attack",
          "text": "강철 검으로 고블린을 공격한다",
          "conditions": [
            {
              "variable": "equipped_weapon",
              "operator": "==",
              "value": "강철 검 (Steel Sword)",
              "fail_message": "검이 없으면 이 강력한 공격을 펼칠 수 없습니다."
            }
          ],
          "effects": [
            {
              "variable": "monster_hp",
              "operator": "-",
              "value": 25
            },
            {
              "variable": "hp",
              "operator": "-",
              "value": 15
            }
          ],
          "message": "당신이 공격했습니다! 고블린 전사에게 25의 데미지를 주었습니다. 고블린 전사가 반격하여 당신은 15의 데미지를 입었습니다."
        },
        {
          "input": "punch",
          "text": "맨손(주먹)으로 고블린을 공격한다",
          "conditions": [
            {
              "variable": "equipped_weapon",
              "operator": "!=",
              "value": "강철 검 (Steel Sword)",
              "fail_message": "검을 장착 중이므로 주먹 대신 검을 사용하는 것이 낫습니다."
            }
          ],
          "effects": [
            {
              "variable": "monster_hp",
              "operator": "-",
              "value": 5
            },
            {
              "variable": "hp",
              "operator": "-",
              "value": 15
            }
          ],
          "message": "당신이 맨손으로 공격했습니다! 고블린 전사에게 5의 데미지를 주었습니다. 고블린 전사가 반격하여 당신은 15의 데미지를 입었습니다."
        },
        {
          "input": "move west",
          "text": "복도로 퇴각한다",
          "next_scene": "hallway",
          "message": "무서운 고블린을 피해 복도로 후퇴합니다."
        }
      ]
    }
  }
}

NOVEL_CONFIG = {
  "engine_settings": {
    "game_title": "두근두근 고등학교 연애 시뮬레이션",
    "start_scene": "school_gate",
    "start_log": "새 학기가 시작되었습니다. 목표는 3일 동안 호감도를 쌓아 고백에 성공하는 것입니다!",
    "status_bar_template": "날짜: {day}/{max_days}일차 | 호감도: {love} | 타겟: {name}"
  },
  "initial_state": {
    "variables": {
      "day": 1,
      "max_days": 3,
      "love": 0,
      "name": "한유리"
    }
  },
  "scenes": {
    "school_gate": {
      "title": "학교 정문 앞 (School Gate)",
      "description": "봄바람이 부는 학교 교문 앞입니다. 평소 짝사랑하던 {name}가 친구를 기다리는지 서성이고 있습니다. 어떻게 다가갈까요?",
      "choices": [
        {
          "input": "1",
          "text": "밝은 미소로 인사를 건넨다",
          "effects": [
            {
              "variable": "love",
              "operator": "+",
              "value": 15
            },
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "next_scene": "classroom",
          "message": "유리에게 인사를 건네자 밝게 받아줍니다. '안녕! 오늘 날씨 진짜 좋다, 그치?' (호감도 +15)"
        },
        {
          "input": "2",
          "text": "부끄러우니 서둘러 교실로 피해 간다",
          "effects": [
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "next_scene": "classroom",
          "message": "눈을 마주치지 못하고 서둘러 교실로 뛰어갔습니다. 유리가 당신을 쳐다본 것 같기도 합니다... (호감도 변동 없음)"
        }
      ]
    },
    "classroom": {
      "title": "조용한 방과 후 교실 (Classroom)",
      "description": "2일차 방과 후, 조용한 교실입니다. {name}가 자리에 홀로 남아 어려운 수학 문제를 풀며 한숨을 쉬고 있습니다.",
      "choices": [
        {
          "input": "1",
          "text": "수학 공식을 친절히 설명해 준다",
          "effects": [
            {
              "variable": "love",
              "operator": "+",
              "value": 20
            },
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "next_scene": "roof",
          "message": "유리가 눈을 반짝이며 감탄합니다. '와! 이거 진짜 어려웠는데 한 번에 이해됐어! 고마워!' (호감도 +20)"
        },
        {
          "input": "2",
          "text": "차가운 초코우유를 슬쩍 건넨다",
          "effects": [
            {
              "variable": "love",
              "operator": "+",
              "value": 10
            },
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "next_scene": "roof",
          "message": "유리가 미소를 지으며 초코우유를 마십니다. '고마워! 마침 당 떨어졌는데 타이밍 예술이네.' (호감도 +10)"
        },
        {
          "input": "3",
          "text": "귀찮으니 그냥 가방을 싸고 조용히 하교한다",
          "effects": [
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "next_scene": "roof",
          "message": "유리에게 방해가 되지 않게 가만히 교실을 빠져나왔습니다."
        }
      ]
    },
    "roof": {
      "title": "붉게 물든 노을 아래 옥상 (School Roof)",
      "description": "3일차 방과 후, 붉은 노을이 비치는 옥상입니다. 바람에 벚꽃 잎이 흩날립니다. 당신의 고백을 기다리는 듯 {name}가 상기된 얼굴로 서 있습니다. 이제 운명의 순간입니다.",
      "auto_rules": [
        {
          "conditions": [
            {
              "variable": "day",
              "operator": ">",
              "value": 3
            },
            {
              "variable": "love",
              "operator": ">=",
              "value": 30
            }
          ],
          "game_over": True,
          "ending": "won",
          "message": "당신의 진솔한 마음을 들은 유리가 부끄러워하며 웃습니다. '나도 실은 네가 언제 말해주나 기다렸어... 좋아해!' (연애 성공! 해피 엔딩)"
        },
        {
          "conditions": [
            {
              "variable": "day",
              "operator": ">",
              "value": 3
            },
            {
              "variable": "love",
              "operator": "<",
              "value": 30
            }
          ],
          "game_over": True,
          "ending": "lost",
          "message": "유리가 조심스럽게 대답합니다. '마음은 고맙지만... 난 널 좋은 친구로만 생각하고 있었어. 미안해.' (실연... 배드 엔딩)"
        }
      ],
      "choices": [
        {
          "input": "1",
          "text": "꽃다발을 내밀며 정식으로 사귀자고 고백한다",
          "effects": [
            {
              "variable": "day",
              "operator": "+",
              "value": 1
            }
          ],
          "message": "마음을 담아 진지하게 '유리야, 나랑 사귀어 줄래?'라고 고백했습니다..."
        }
      ]
    }
  }
}

QUIZ_CONFIG = {
  "engine_settings": {
    "game_title": "서바이벌 퀴즈 쇼 (Survival Quiz)",
    "start_scene": "q1",
    "start_log": "퀴즈 쇼에 오신 것을 환영합니다! 3문제를 모두 풀고 살아남아 챔피언에 도전하세요.",
    "status_bar_template": "점수: {score}점 | 남은 목숨(Life): {life}개"
  },
  "initial_state": {
    "variables": {
      "score": 0,
      "life": 3
    }
  },
  "scenes": {
    "q1": {
      "title": "1단계 퀴즈 (Question 1)",
      "description": "퀴즈 1단계: '지구상에서 가장 넓은 면적을 차지하는 바다는 어디일까요?'",
      "auto_rules": [
        {
          "conditions": [
            {
              "variable": "life",
              "operator": "<=",
              "value": 0
            }
          ],
          "game_over": True,
          "ending": "lost",
          "message": "목숨이 모두 소진되었습니다... 탈락하셨습니다."
        }
      ],
      "choices": [
        {
          "input": "1",
          "text": "태평양 (Pacific Ocean)",
          "effects": [
            {
              "variable": "score",
              "operator": "+",
              "value": 10
            }
          ],
          "next_scene": "q2",
          "message": "정답입니다! 태평양은 가장 넓은 대양입니다. (+10점)"
        },
        {
          "input": "2",
          "text": "대서양 (Atlantic Ocean)",
          "effects": [
            {
              "variable": "life",
              "operator": "-",
              "value": 1
            }
          ],
          "next_scene": "q2",
          "message": "오답입니다! 대서양은 두 번째로 넓은 바다입니다. (목숨 -1)"
        },
        {
          "input": "3",
          "text": "인도양 (Indian Ocean)",
          "effects": [
            {
              "variable": "life",
              "operator": "-",
              "value": 1
            }
          ],
          "next_scene": "q2",
          "message": "오답입니다! 인도양은 세 번째로 넓은 바다입니다. (목숨 -1)"
        }
      ]
    },
    "q2": {
      "title": "2단계 퀴즈 (Question 2)",
      "description": "퀴즈 2단계: '인류 역사상 달에 최초로 착륙한 우주선은 무엇일까요?'",
      "auto_rules": [
        {
          "conditions": [
            {
              "variable": "life",
              "operator": "<=",
              "value": 0
            }
          ],
          "game_over": True,
          "ending": "lost",
          "message": "목숨이 모두 소진되었습니다... 탈락하셨습니다."
        }
      ],
      "choices": [
        {
          "input": "1",
          "text": "아폴로 11호 (Apollo 11)",
          "effects": [
            {
              "variable": "score",
              "operator": "+",
              "value": 10
            }
          ],
          "next_scene": "q3",
          "message": "정답입니다! 1969년 닐 암스트롱이 아폴로 11호를 타고 달에 착륙했습니다. (+10점)"
        },
        {
          "input": "2",
          "text": "보이저 1호 (Voyager 1)",
          "effects": [
            {
              "variable": "life",
              "operator": "-",
              "value": 1
            }
          ],
          "next_scene": "q3",
          "message": "오답입니다! 보이저 1호는 외행성 무인 탐사선입니다. (목숨 -1)"
        },
        {
          "input": "3",
          "text": "아폴로 13호 (Apollo 13)",
          "effects": [
            {
              "variable": "life",
              "operator": "-",
              "value": 1
            }
          ],
          "next_scene": "q3",
          "message": "오답입니다! 아폴로 13호는 산소탱크 사고로 착륙하지 못하고 무사 귀환만 성공했습니다. (목숨 -1)"
        }
      ]
    },
    "q3": {
      "title": "최종 3단계 퀴즈 (Final Question)",
      "description": "퀴즈 최종 단계: '물과 기름처럼 서로 잘 섞이지 않고 물을 배척하는 화학적 성질은?'",
      "auto_rules": [
        {
          "conditions": [
            {
              "variable": "life",
              "operator": "<=",
              "value": 0
            }
          ],
          "game_over": True,
          "ending": "lost",
          "message": "오답의 여파로 목숨이 0개가 되었습니다... 아쉽게 최종 단계에서 탈락하셨습니다."
        },
        {
          "conditions": [
            {
              "variable": "life",
              "operator": ">",
              "value": 0
            },
            {
              "variable": "score",
              "operator": ">=",
              "value": 40
            }
          ],
          "game_over": True,
          "ending": "won",
          "message": "축하합니다! 퀴즈를 모두 맞히고 40점 만점으로 퀴즈 챔피언에 등극하셨습니다!"
        },
        {
          "conditions": [
            {
              "variable": "life",
              "operator": ">",
              "value": 0
            },
            {
              "variable": "score",
              "operator": "<",
              "value": 40
            }
          ],
          "game_over": True,
          "ending": "won",
          "message": "최종 통과에 성공했습니다! 비록 만점은 아니지만 훌륭한 실력이네요. (최종 점수: {score}점)"
        }
      ],
      "choices": [
        {
          "input": "1",
          "text": "친수성 (Hydrophilic)",
          "effects": [
            {
              "variable": "life",
              "operator": "-",
              "value": 1
            }
          ],
          "message": "오답입니다! 친수성은 물과 친한 성질을 뜻합니다."
        },
        {
          "input": "2",
          "text": "소수성 (Hydrophobic)",
          "effects": [
            {
              "variable": "score",
              "operator": "+",
              "value": 20
            }
          ],
          "message": "정답입니다! 소수성은 물을 싫어하는 성질입니다. (+20점)"
        }
      ]
    }
  }
}

GENRES = {
    "1": ("던전 탐험 RPG", RPG_CONFIG),
    "2": ("연애 시뮬레이션", NOVEL_CONFIG),
    "3": ("서바이벌 퀴즈 쇼", QUIZ_CONFIG)
}

def run_command(cmd_arg, config_data, state_data):
    try:
        result = subprocess.run(
            [
                "python3", "text-game/scripts/game_engine.py", 
                "--command", cmd_arg,
                "--config-data", json.dumps(config_data, ensure_ascii=False),
                "--state-data", json.dumps(state_data, ensure_ascii=False)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def init_game(config_data):
    try:
        result = subprocess.run(
            [
                "python3", "text-game/scripts/game_engine.py", 
                "--init",
                "--config-data", json.dumps(config_data, ensure_ascii=False),
                "--state-data", "{}"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"초기화 오류 발생: {e}")
        return None

def render_ui(data):
    if not data:
        return
    
    ui = data.get("ui_display")
    if not ui:
        print(f"에러 메시지: {data.get('message', '알 수 없는 오류')}")
        return
        
    print("\n" + "="*50)
    print(f"🎮  {ui['room_title']}")
    print(f" 설명: {ui['room_description']}")
    print("-"*50)
    print(f"📋  상태 정보: {ui['status_bar']}")
    print("-"*50)
    print("📰  최근 이벤트:")
    for log in ui['logs']:
        print(f"  * {log}")
    print("-"*50)
    print("💡  선택 가능한 행동:")
    for action in ui['available_actions']:
        print(f"  - {action}")
    print("="*50)

def main():
    print("*"*50)
    print(" 무상태 실시간 텍스트 게임 플레이어 (디스크 저장 없음)")
    print("*"*50)
    print("플레이할 게임 장르를 선택하세요:")
    for key, (name, _) in GENRES.items():
        print(f" [{key}] {name}")
    print("*"*50)
    
    choice = ""
    while choice not in GENRES:
        choice = input("선택 (1~3): ").strip()
        
    genre_name, config_data = GENRES[choice]
    print(f"\n🚀 {genre_name}을 시작합니다...")
    
    data = init_game(config_data)
    if not data or not data.get("success"):
        print("게임을 초기화하지 못했습니다.")
        sys.exit(1)
        
    render_ui(data)
    # 메모리에서 관리할 상태(state) 정보
    game_state = data.get("game_state")
    
    while True:
        try:
            user_input = input("\n행동 입력 (종료: 'exit', 상태창: 'status', 관찰: 'look'): ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'exit':
                print("게임을 종료합니다.")
                break
                
            # 명령어 처리 실행 (메모리의 config_data와 game_state를 매 턴 전달)
            data = run_command(user_input, config_data, game_state)
            if data:
                if not data.get("success"):
                    print(f"\n⚠️  경고: {data.get('message')}")
                else:
                    render_ui(data)
                    # 반환받은 game_state를 다음 턴을 위해 메모리에 업데이트
                    game_state = data.get("game_state")
                    
                if data.get("game_over"):
                    ending = data.get("ending")
                    print(f"\n🏁 게임이 최종 종료되었습니다. (결과: {ending.upper()})")
                    break
        except KeyboardInterrupt:
            print("\n게임을 중단합니다.")
            break

if __name__ == "__main__":
    main()
