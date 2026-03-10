import json
import os

from openai import OpenAI

from prompt import system_msg, tools_msg
from tools import draw_image, generate_3d_model, textured_3d_model


def _try_load_local_key_module() -> None:
    try:
        import key  # noqa: F401
    except ImportError:
        print("warn: please set DASHSCOPE_API_KEY in environment")


def _execute_tool_call(func_name: str, arguments: dict, asset_list: list) -> str:
    if func_name == "push_asset_list":
        value = arguments.get("string")
        if value is None:
            return "missing parameter: string"
        asset_list.append(value)
        print("insert", value)
        return "success"

    if func_name == "get_asset_list_item":
        n = arguments.get("n")
        if not isinstance(n, int):
            return "parameter n must be an integer"
        if n < 0 or n >= len(asset_list):
            return f"index out of range: {n}"
        item = asset_list[n]
        print(item)
        return str(item)

    if func_name == "len_asset_list":
        length = len(asset_list)
        print("asset_list length:", length)
        return str(length)

    if func_name == "list_asset_list":
        print(asset_list)
        return str(asset_list)

    if func_name == "pop_asset_list":
        if not asset_list:
            return "asset_list is empty"
        item = asset_list.pop(0)
        print(item)
        return str(item)

    if func_name == "clear_asset_list":
        asset_list.clear()
        print("asset_list cleared")
        return "success"

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

    asset_list = []
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

                tool_result = _execute_tool_call(func_name, arguments, asset_list)

                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result,
                }
                messages.append(tool_message)
                chat_lock = False


if __name__ == "__main__":
    main()
