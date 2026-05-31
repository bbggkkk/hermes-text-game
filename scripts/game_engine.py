import json
import argparse
import sys
import copy

# 전역 게임 설정 데이터
CONFIG = {}

def load_game_config(config_data_str):
    global CONFIG
    if not config_data_str:
        print(json.dumps({
            "success": False,
            "message": "--config-data 인자가 누락되었습니다. 게임 기획/설정 데이터를 JSON 문자열로 주입해야 합니다.",
            "ui_display": None,
            "game_state": None
        }, ensure_ascii=False))
        sys.exit(1)
        
    try:
        CONFIG = json.loads(config_data_str)
    except Exception as e:
        print(json.dumps({
            "success": False,
            "message": f"CONFIG JSON 파싱 중 오류가 발생했습니다: {e}",
            "ui_display": None,
            "game_state": None
        }, ensure_ascii=False))
        sys.exit(1)

def format_text(text, variables):
    if not text:
        return ""
    formatted = text
    for k, v in variables.items():
        placeholder = f"{{{k}}}"
        if placeholder in formatted:
            if isinstance(v, list):
                val_str = ", ".join(v) if v else "없음"
            else:
                val_str = str(v)
            formatted = formatted.replace(placeholder, val_str)
    return formatted

def check_condition(cond, variables):
    var_name = cond.get("variable")
    operator = cond.get("operator")
    target_value = cond.get("value")
    
    if var_name not in variables:
        return False
        
    current_value = variables[var_name]
    
    if operator == "==":
        return current_value == target_value
    elif operator == "!=":
        return current_value != target_value
    elif operator == ">":
        return current_value > target_value
    elif operator == ">=":
        return current_value >= target_value
    elif operator == "<":
        return current_value < target_value
    elif operator == "<=":
        return current_value <= target_value
    elif operator == "contains":
        if isinstance(current_value, list):
            return target_value in current_value
        return target_value in str(current_value)
    elif operator == "not_contains":
        if isinstance(current_value, list):
            return target_value not in current_value
        return target_value not in str(current_value)
    return False

def apply_effect(effect, variables):
    var_name = effect.get("variable")
    operator = effect.get("operator")
    val = effect.get("value")
    
    if var_name not in variables:
        if isinstance(val, int):
            variables[var_name] = 0
        elif isinstance(val, list):
            variables[var_name] = []
        else:
            variables[var_name] = ""
            
    if operator == "=":
        variables[var_name] = copy.deepcopy(val)
    elif operator == "+":
        if isinstance(variables[var_name], (int, float)) and isinstance(val, (int, float)):
            variables[var_name] += val
    elif operator == "-":
        if isinstance(variables[var_name], (int, float)) and isinstance(val, (int, float)):
            variables[var_name] -= val
    elif operator == "append":
        if not isinstance(variables[var_name], list):
            variables[var_name] = []
        if val not in variables[var_name]:
            variables[var_name].append(val)
    elif operator == "remove":
        if isinstance(variables[var_name], list) and val in variables[var_name]:
            variables[var_name].remove(val)

def get_initial_state():
    engine_settings = CONFIG.get("engine_settings", {})
    init_state_cfg = CONFIG.get("initial_state", {})
    
    start_scene = engine_settings.get("start_scene", "start")
    variables = copy.deepcopy(init_state_cfg.get("variables", {}))
    start_log = engine_settings.get("start_log", "게임이 시작되었습니다.")
    
    return {
        "player": {
            "current_scene": start_scene,
            "status": "playing",
            "variables": variables
        },
        "logs": [start_log]
    }

def load_game_state(state_data_str=None):
    if state_data_str:
        try:
            return json.loads(state_data_str)
        except Exception:
            return get_initial_state()
    return get_initial_state()

def make_json_output(success, message, state):
    player = state["player"]
    current_scene_id = player["current_scene"]
    scenes = CONFIG.get("scenes", {})
    scene_data = scenes.get(current_scene_id)
    variables = player.get("variables", {})
    engine_settings = CONFIG.get("engine_settings", {})
    
    if not scene_data:
        return json.dumps({
            "success": False,
            "message": f"씬 데이터를 찾을 수 없습니다: {current_scene_id}",
            "ui_display": None,
            "game_state": None
        }, ensure_ascii=False)
        
    room_title = format_text(scene_data.get("title", current_scene_id), variables)
    room_description = format_text(scene_data.get("description", ""), variables)
    
    status_bar_template = engine_settings.get("status_bar_template", "상태: {status}")
    status_bar = format_text(status_bar_template, variables)
    
    available_actions = []
    choices = scene_data.get("choices", [])
    for idx, choice in enumerate(choices):
        conditions = choice.get("conditions", [])
        met = True
        failed_reason = ""
        
        for cond in conditions:
            if not check_condition(cond, variables):
                met = False
                failed_reason = cond.get("fail_message", "조건 미충족")
                break
                
        choice_text = format_text(choice.get("text", ""), variables)
        choice_input = choice.get("input", str(idx + 1))
        
        if met:
            available_actions.append(f"{choice_input} ({choice_text})")
        else:
            available_actions.append(f"{choice_input} (비활성화 - {failed_reason})")

    output = {
        "success": success,
        "message": message,
        "game_over": player["status"] in ["won", "lost"],
        "ending": player["status"],
        "ui_display": {
            "room_title": room_title,
            "room_description": room_description,
            "status_bar": status_bar,
            "available_actions": available_actions,
            "logs": state["logs"][-3:]
        },
        "game_state": state
    }
    return json.dumps(output, ensure_ascii=False, indent=2)

def process_command(state, command_str):
    command_str = command_str.strip().lower()
    player = state["player"]
    current_scene_id = player["current_scene"]
    scenes = CONFIG.get("scenes", {})
    scene_data = scenes.get(current_scene_id)
    variables = player["variables"]
    
    if player["status"] != "playing":
        if command_str == "reset":
            pass
        else:
            return False, f"게임이 이미 종료되었습니다. 결과: {player['status'].upper()}. 'reset'을 입력하여 다시 시작하십시오."

    if command_str == "reset":
        new_state = get_initial_state()
        state.update(new_state)
        state["logs"] = ["게임을 초기화했습니다. 처음부터 다시 시작합니다."]
        return True, "게임을 초기화했습니다."

    elif command_str == "look":
        state["logs"].append("주변을 다시 살펴보았습니다.")
        return True, "씬을 관찰했습니다."

    elif command_str == "status":
        status_log = "현재 상태 변수: " + ", ".join([f"{k}: {v}" for k, v in variables.items()])
        state["logs"].append(status_log)
        return True, "상태 변수를 조회했습니다."

    choices = scene_data.get("choices", [])
    matched_choice = None
    
    for idx, choice in enumerate(choices):
        choice_input = str(choice.get("input", "")).strip().lower()
        choice_text = str(choice.get("text", "")).strip().lower()
        
        if command_str == choice_input or command_str == choice_text or command_str == f"{idx+1}":
            matched_choice = choice
            break
            
    if not matched_choice:
        for choice in choices:
            choice_text = str(choice.get("text", "")).strip().lower()
            if choice_text in command_str or command_str in choice_text:
                matched_choice = choice
                break
                
    if not matched_choice:
        valid_inputs = [str(c.get("input", i+1)) for i, c in enumerate(choices)]
        return False, f"알 수 없는 행동입니다. 가능한 입력: {', '.join(valid_inputs)}, look, status, reset"

    conditions = matched_choice.get("conditions", [])
    for cond in conditions:
        if not check_condition(cond, variables):
            fail_msg = cond.get("fail_message", "행동을 취할 수 있는 조건이 충족되지 않았습니다.")
            return False, fail_msg

    effects = matched_choice.get("effects", [])
    for effect in effects:
        apply_effect(effect, variables)
        
    choice_msg = format_text(matched_choice.get("message", ""), variables)
    if choice_msg:
        state["logs"].append(choice_msg)
        
    next_scene = matched_choice.get("next_scene")
    if next_scene:
        if next_scene in scenes:
            player["current_scene"] = next_scene
        else:
            return False, f"이동하려는 대상 씬({next_scene})이 설정 파일에 존재하지 않습니다."
            
    if matched_choice.get("game_over"):
        player["status"] = matched_choice.get("ending", "won")
        
    scene_data_updated = scenes.get(player["current_scene"], {})
    auto_rules = scene_data_updated.get("auto_rules", [])
    for rule in auto_rules:
        rule_conditions = rule.get("conditions", [])
        rule_met = True
        for r_cond in rule_conditions:
            if not check_condition(r_cond, variables):
                rule_met = False
                break
        
        if rule_met:
            rule_msg = format_text(rule.get("message", ""), variables)
            if rule_msg:
                state["logs"].append(rule_msg)
            rule_next = rule.get("next_scene")
            if rule_next and rule_next in scenes:
                player["current_scene"] = rule_next
            if rule.get("game_over"):
                player["status"] = rule.get("ending", "won")
            break

    return True, choice_msg if choice_msg else "행동이 수행되었습니다."

def main():
    parser = argparse.ArgumentParser(description="Hermes Universal Stateless Text Game Engine")
    parser.add_argument("--command", type=str, help="플레이어의 게임 행동 입력")
    parser.add_argument("--init", action="store_true", help="게임을 초기 상태로 셋업")
    
    # 100% 실시간 메모리 데이터로만 구성하도록 설정 인자 정리
    parser.add_argument("--config-data", type=str, required=True, help="실시간 CONFIG JSON 문자열 데이터")
    parser.add_argument("--state-data", type=str, help="실시간 STATE JSON 문자열 데이터")
    
    args = parser.parse_args()

    # CONFIG 로드 (100% 메모리 주입 강제)
    load_game_config(args.config_data)

    # STATE 로드 (메모리 주입 우선, 없으면 초기 셋업)
    state = load_game_state(args.state_data)

    if args.init:
        state = get_initial_state()
        print(make_json_output(True, "새로운 게임을 시작합니다.", state))
        sys.exit(0)

    if not args.command:
        print(json.dumps({
            "success": False,
            "message": "--command 인자가 필요합니다.",
            "ui_display": None,
            "game_state": None
        }, ensure_ascii=False))
        sys.exit(1)

    # 명령어 처리
    success, message = process_command(state, args.command)
    
    # 세이브 기능은 100% 호출자에게 위임(Bypass), 로컬 디스크 저장은 전혀 수행하지 않음
    print(make_json_output(success, message, state))

if __name__ == "__main__":
    main()
