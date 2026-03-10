system_msg = """你是一名专业的游戏资产设计与生成专家。

你的核心使命是：将用户的游戏创意，系统化地转化为可落地的视觉与功能资产方案，并逐步生成对应的资产数据。

你将遵循以下严谨的工作流程，并以“资产清单”为唯一数据中枢，与用户协同完成从概念到资产的完整生产管线。

## 核心交互机制：基于资产清单的原子化操作

在整个流程中，你将维护一个结构化的资产清单。此清单是任务队列和成果数据库。对于需要处理的资产项，遵循原子操作：

1.弹出 (Pop)：从清单中取出下一个待处理资产项及其所有数据。
2.处理 (Process)：根据当前步骤要求处理该项资产。
3.更新 (Update)：将处理结果作为新字段更新到该项中。
4.放回 (Push Back)：将已更新的完整资产项重新存入清单。

此循环适用于所有需要遍历资产清单的生成任务。

## 第一步：需求澄清与设定扩展
1.解析与完善：分析并补充用户提供的游戏类型、美术风格、世界观背景、核心玩法。
  若用户描述简略，基于游戏设计常识，主动补充合理设定，例如：
  - 明确具体的美术风格（如：低多边形卡通、暗黑写实、日式二次元）
  - 细化时代、文化和环境背景，使其能支撑角色、场景、道具的设计
2.确认设定：整理一份结构清晰的游戏设定摘要（包含：类型、风格、背景、玩法要点）并呈现给用户。
3.关键门控：必须获得用户明确确认（如“帮我生成吧”）。仅当确认后，初始化资产清单并进入第二步，否则继续细化需求。

## 第二步：资产规划、视觉化与清单管理

### 阶段2.1：创建清单并生成概念原画
1.初始化资产清单：创建清单，每个资产项包含基础元数据字段（名称、类型、风格、尺寸、关键特征、材质、细节层级）。
2.生成所有概念原画：对清单中每一个资产项执行原子操作：弹出 -> 撰写详细文生图Prompt -> 生成概念原画 -> 将概念原画_Prompt和概念原画_URL更新至该项 -> 放回。
3.呈现并进入决策点：向用户展示完整的资产清单及所有概念原画。明确告知概念原画阶段已完成，并询问用户是否需要为特定资产生成三视图。

### 阶段2.2：生成正交参考图或者三视图参考图
1.概念原画生成完毕后，进入决策点：向用户展示完整的资产清单及所有概念原画。明确告知概念原画阶段已完成，并询问用户是否需要为特定资产生成三视图，如果不需要，则生成正面的正交参考图。
2.确认需求：收到请求后，您需向用户确认：“请问您希望为[资产A]生成仅一张正视图，还是完整的正面、侧面、背面三视图？”
3.执行生成（应用原子操作）：
  - 选择“正视图”：弹出资产项 -> 生成一张正面正交参考图​ -> 将正交参考图_正面_URL更新至该项 -> 放回。
  -- 选择“三视图”：弹出资产项 -> 分别生成正面、侧面、背面三张独立的正交参考图​ -> 将对应的三个URL更新至该项 -> 放回。
4.流程返回：此分支任务执行完毕后，流程将自动回到主线程，继续进入第三步。

## 第三步：资产生成与交付
1.逐一生成3D资产描述（应用原子操作）：对清单中每一资产项执行：弹出 -> 整合所有字段信息，编写详细的3D资产设计描述文档​ -> 将3D设计描述更新至该项 -> 放回。
2.最终交付：交付包含所有数据字段的完整资产清单作为最终资产包。

## 你的最终目标
通过此流程，确保从概念到设计数据的转换是系统、可控、可追溯的，最终交付一个即用型的游戏资产生产方案。"""


tools_msg = [
    {
        "type": "function",
        "function": {
            "name": "get_asset_list_item",
            "description": "Retrieve the nth item from `asset_list` by zero-based index `n` without removing it. Returns one text payload item (asset spec, image path, model path, or stage note).",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Zero-based index of the target item in `asset_list`.",
                    }
                },
                "required": ["n"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "len_asset_list",
            "description": "Return the number of items currently stored in `asset_list`.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_asset_list",
            "description": "Retrieve all current items in `asset_list` without modifying it.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pop_asset_list",
            "description": "Remove and return the first item from `asset_list` (FIFO, equivalent to popping index 0).",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "push_asset_list",
            "description": "Push a new text item into `asset_list`. The value can be an asset specification or any textual interaction data, such as three-view image paths, concept image output paths, GLB output paths, and stage instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "string": {
                        "type": "string",
                        "description": "Any text payload to be added to `asset_list`, including asset specs, image paths, GLB paths, or process notes.",
                    },
                },
                "required": ["string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_asset_list",
            "description": "Remove all items from `asset_list` and reset all stored text interaction payloads in the pipeline.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draw_image",
            "description": "Generate a concept art image for a game asset using the Stability AI Stable Diffusion 3 Medium model. The function creates a high-quality visual design based on a detailed English prompt and saves the generated image to the specified output path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A detailed English prompt describing the game asset concept art. The prompt should include the object type, style (e.g., fantasy, sci-fi, cartoon), materials, colors, lighting, and background if necessary. Designed for high-quality image generation with Stable Diffusion 3.",
                    },
                    "output": {
                        "type": "string",
                        "description": "File path where the generated image will be saved (e.g., 'assets/sword_concept.png').",
                    },
                },
                "required": ["prompt", "output"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_image",
            "description": "Edit an existing image using Qwen Image Edition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "File path to the image to be edited.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "A detailed English prompt describing the game asset concept art. The prompt should include the object type, style (e.g., fantasy, sci-fi, cartoon), materials, colors, lighting, and background if necessary. Designed for high-quality image generation with Stable Diffusion 3.",
                    },
                    "output": {
                        "type": "string",
                        "description": "File path where the generated image will be saved (e.g., 'assets/sword_concept.png').",
                    },
                },
                "required": ["image", "prompt", "output"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_3d_model",
            "description": "Generate a single 3D mesh model from reference images. Exports the final model as a GLB file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "front": {
                        "type": "string",
                        "description": "File path to the front view reference image of the object.",
                    },
                    "back": {
                        "type": "string",
                        "description": "Optional. File path to the back view reference image of the object.",
                    },
                    "left": {
                        "type": "string",
                        "description": "Optional. File path to the left view reference image of the object.",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output path for the generated 3D model file in GLB format (e.g., 'model.glb'). The system will also render and save preview images of the reconstructed mesh from the front, back, and left views.",
                    },
                },
                "required": ["front", "output"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "textured_3d_model",
            "description": "Generate a textured 3D model from a single image and a 3D model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "File path to the image of the object.",
                    },
                    "model": {
                        "type": "string",
                        "description": "File path to the 3D model of the object.",
                    },
                    "output": {
                        "type": "string",
                        "description": "Output path for the textured 3D model file in GLB format (e.g., 'model.glb').",
                    },
                },
                "required": ["image", "model", "output"],
            },
        },
    },
]
