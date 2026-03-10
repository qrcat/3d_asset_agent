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

### 阶段 2.2：生成正交参考图
#### 【图像生成标准】
所有生成的正交参考图必须严格满足以下条件：
- 背景要求：使用纯色或纯白背景。
  Prompt 参考：`Replace the background with a solid color or white background`
- 主体要求：每个视图仅包含单一人物或单一物品。人物需为标准**T-Pose**；人物/物品必须完整呈现，不得出现无关杂物。
- 光照要求：采用均匀平光（Flat lighting），禁止阴影、高光及复杂光影效果。
#### 【标准执行流程】
1.阶段结算与需求确认
在概念原画生成完成后，向用户展示完整资产清单与全部概念原画，并明确告知：“概念原画阶段已结束”。
随后主动确认参考图生成规格：
> “请问您希望为以上资产生成**单张正视图参考图**，还是**完整的正面、侧面、背面三视图**？”
说明：若用户明确表示不需要三视图，或未作具体说明，则默认按**单张正视图**处理。
生成正视图时，需确保主体位于画面中心；仅正视图需要加入主体控制描述，侧视图与背视图无需额外主体控制描述。
2.调用工具执行生成
根据用户确认结果，使用`edit_image`工具执行：
- 分支 A：单张正视图
  以概念原画为输入，生成一张正视图正交参考图。（Prompt 参考：[`Obtain the front view`]）
- 分支 B：完整三视图
  a.以概念原画为输入，生成正视图正交参考图（`Obtain the front view`）；
  b.基于该正视图，生成侧面正交参考图（`Obtain the left-side`）；
  c.基于该正视图，生成背面正交参考图（`Obtain the back-side`）。
3.流程推进
当前资产的参考图生成任务完成后，自动结束本阶段，并引导流程进入**第三阶段**。


## 第三步：资产生成与交付
1.逐一生成3D资产描述（应用原子操作）：对清单中每一资产项执行：弹出 -> 整合所有字段信息，编写详细的3D资产设计描述文档​ -> 将3D设计描述更新至该项 -> 放回。
2.最终交付：交付包含所有数据字段的完整资产清单作为最终资产包。

## 你的最终目标
通过此流程，确保从概念到设计数据的转换是系统、可控、可追溯的，最终交付一个即用型的游戏资产生产方案。"""


tools_msg = [
    {
        "type": "function",
        "function": {
            "name": "opt_list",
            "description": "Unified list operation tool for `asset_list`. Supports `push`, `pop`, `get`, `len`, `clear`, and `list` on the list identified by `name`.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Target list name, use `asset_list`.",
                    },
                    "opterate": {
                        "type": "string",
                        "description": "Operation to execute. One of: `push`, `pop`, `get`, `len`, `clear`, `list`.",
                    },
                    "string": {
                        "type": "string",
                        "description": "Required when `opterate` is `push`: string value to append.",
                    },
                    "n": {
                        "type": "integer",
                        "description": "Required when `opterate` is `get`: zero-based index.",
                    },
                },
                "required": ["name", "opterate"],
            },
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
            "description": "Edit an existing image using Image Edition. Use this tool when generating orthographic views from an existing concept art.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "File path to the image to be edited.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "A detailed English prompt describing the game asset concept art. The prompt should include the object type, style (e.g., fantasy, sci-fi, cartoon), materials, colors, lighting, and background if necessary. Designed for high-quality image generation with Image Edition.",
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
