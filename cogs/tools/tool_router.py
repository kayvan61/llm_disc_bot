
import cogs.tools.get_current_temp as get_current_temp
import logging

logger = logging.getLogger(__name__)

TOOL_LIST = {
    # get_current_tempurature
    "get_current_tempurature": {
        "type": "function",
        "function": {
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get the temperature for, in the format \"City, State, Country\"."
                    },
                },
                "required": [
                "location"
                ]
            }
        },
        "callable": get_current_temp.call_tool,
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
        logging.info(f"importing tool: {k} with desc: {tool_desc}")
        ret.append(tool_desc)

    return ret

def get_all_tool_names():
    return list(TOOL_LIST.keys())

async def route_tool(tool_name:str, **kwargs) -> str:
    logging.info(f"got arguments: {kwargs}")
    return await TOOL_LIST[tool_name]["callable"](**kwargs)


