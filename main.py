from prompt import system_msg, tools_msg
from tools import draw_image, generate_3d_model, textured_3d_model

import json
import os

from openai import OpenAI
from collections import defaultdict


def _try_load_local_key_module() -> None:
    try:
        import key  # noqa: F401
    except ImportError:
        print("warn: please set DASHSCOPE_API_KEY in environment")


def opt_list(collect: defaultdict, name: str, opterate: str, **arguments):
    asset_list: list = collect[name]

    if opterate == "push":
        value = arguments.get("string")
        if not isinstance(value, str):
            return "parameter string must be a string"
        asset_list.append(value)
        return "success"
    elif opterate == "pop":
        if asset_list:
            return asset_list.pop(0)
        else:
            return "asset_list is empty"
    elif opterate == "get":
        n = arguments.get("n")
        if not isinstance(n, int):
            return "parameter n must be an integer"
        if n < 0 or n >= len(asset_list):
            return f"index out of range: {n}"
        item = asset_list[n]
        return str(item)
    elif opterate == "len":
        return str(len(asset_list))
    elif opterate == "clear":
        asset_list.clear()
        return "success"
    elif opterate == "list":
        return str(asset_list)


def _execute_tool_call(func_name: str, arguments: dict, collects: list) -> str:
    if func_name == "opt_list":
        return opt_list(collects, **arguments)

    if func_name == "draw_image":
        draw_image(arguments["prompt"], arguments["output"])
        return "success"

    if func_name == "generate_3d_model":
        generate_3d_model(**arguments)
        return "success"

    if func_name == "textured_3d_model":
        textured_3d_model(arguments["image"], arguments["model"], arguments["output"])
        return "success"

    return "unknown function"


def main() -> None:
    _try_load_local_key_module()

    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    collects = defaultdict(list)
    messages = [{"role": "system", "content": system_msg}]
    chat_lock = True

    while True:
        if chat_lock:
            user_input = input("Input: ")
            messages.append({"role": "user", "content": user_input})
        else:
            chat_lock = True

        completion = client.chat.completions.create(
            # model list: https://help.aliyun.com/zh/model-studio/getting-started/models
            model="qwen3.5-plus",
            messages=messages,
            tools=tools_msg,
        )

        assistant_message = completion.choices[0].message
        print(assistant_message.content)
        messages.append(assistant_message)

        if assistant_message.tool_calls is not None:
            for tool_call in assistant_message.tool_calls:
                tool_call_id = tool_call.id
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                tool_result = _execute_tool_call(func_name, arguments, collects)

                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result,
                }
                messages.append(tool_message)
                chat_lock = False


if __name__ == "__main__":
    main()
