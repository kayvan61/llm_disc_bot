
import cogs.tools.get_current_temp as get_current_temp
import cogs.tools.python_interpreter as py_inter
import logging

logger = logging.getLogger(__name__)

TOOL_LIST = {
    # get_current_tempurature
    "get_current_weather": {
        "type": "function",
        "function": {
            "description": "Get current weather at a location. returns just the tempurate in that location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get the weather for, in the format \"City, State, Country\"."
                    },
                },
                "required": [
                "location"
                ]
            }
        },
        "callable": get_current_temp.call_tool,
    },
    "run_python_interpreter": {
        "type": "function",
        "function": {
            "description": "Get the output of a python program. Useful for running simulations, rolling dice, or otherwise checking python output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_code": {
                        "type": "string",
                        "description": "The python script that should be executed."
                    },
                    "dependencies": {
                        "type": "string",
                        "description": "Any dependencies that need to be installed before hand. Formatted as a comma seperated list.",
                    }
                },
                "required": [
                "user_code",
                "dependencies",
                ]
            }
        },
        "callable": py_inter.call_tool,
    },
}

def open_ai_tool_list():
    import copy
    import json

    ret = []
    for k, v in TOOL_LIST.items():
        tool_desc = copy.deepcopy(v)
        del tool_desc["callable"]
        tool_desc["function"]["name"] = k
        logger.info(f"importing tool: {k} with desc: {tool_desc}")
        ret.append(tool_desc)

    return ret

def get_all_tool_names():
    return list(TOOL_LIST.keys())

async def route_tool(tool_name:str, **kwargs) -> str:
    logger.info(f"got arguments: {kwargs}")
    return await TOOL_LIST[tool_name]["callable"](**kwargs)


