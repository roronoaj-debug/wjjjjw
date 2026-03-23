# Standard library imports
import ast
import json
import os
import re

# Third-party imports
import requests
import tiktoken
import yaml
from pydantic import BaseModel

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Local imports
from PhotonicsAI.config import CONF, PATH

if load_dotenv:
    load_dotenv()

prompts = {}
try:
    with open(PATH.prompts) as file:
        prompts = yaml.safe_load(file) or {}
except FileNotFoundError:
    print(f"No {PATH.prompts} file found.")

tokenizer = tiktoken.get_encoding("o200k_base")


def get_runtime_llm_config():
    """Read runtime LLM configuration from session state, config, and env vars."""
    session_model = ""
    session_api_key = ""
    session_base_url = ""

    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx(suppress_warning=True) is not None:
            session_model = str(st.session_state.get("selected_model", "") or "")
            session_api_key = str(st.session_state.get("llm_api_key", "") or "")
            session_base_url = str(st.session_state.get("llm_base_url", "") or "")
    except Exception:
        pass

    model = (
        session_model.strip()
        or CONF.llm_model.strip()
        or os.getenv("LLM_MODEL", "").strip()
        or "glm-4-flash"
    )
    api_key = (
        session_api_key.strip()
        or CONF.llm_api_key.strip()
        or os.getenv("LLM_API_KEY", "").strip()
    )
    base_url = (
        session_base_url.strip()
        or CONF.llm_base_url.strip()
        or os.getenv("LLM_BASE_URL", "").strip()
    )

    return {
        "model": model,
        "api_key": api_key,
        "base_url": base_url,
    }


def get_session_token_usage():
    """Get token usage from current session state."""
    import streamlit as st

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {
            "non_cached_input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
        }
    return st.session_state.token_usage


def reset_token_usage():
    """Reset token usage counters for current session."""
    import streamlit as st

    st.session_state.token_usage = {
        "non_cached_input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
    }


def get_token_usage():
    """Get current token usage for current session."""
    return get_session_token_usage().copy()


def add_token_usage(input_tokens, output_tokens, is_cached=False):
    """Add token usage to the current session counter."""
    token_usage = get_session_token_usage()
    if is_cached:
        token_usage["cached_input_tokens"] += input_tokens
    else:
        token_usage["non_cached_input_tokens"] += input_tokens
    token_usage["output_tokens"] += output_tokens


def debug_token_usage():
    """Debug function to print current session token usage."""
    import streamlit as st

    token_usage = get_token_usage()
    print(f"Current session token usage: {token_usage}")
    if hasattr(st.session_state, "_session_id"):
        print(f"Session ID: {st.session_state._session_id}")


def truncate_prompt(prompt, max_tokens=120000):
    """Truncate the input prompt to the maximum allowed tokens."""
    tokens = tokenizer.encode(prompt)
    if len(tokens) > max_tokens:
        tokens = tokens[-max_tokens:]
        return tokenizer.decode(tokens)
    return prompt


def _normalize_components_list(data):
    """规范化 components_list 字段。"""
    try:
        if isinstance(data, dict) and isinstance(data.get("components_list"), list):
            def _dict_to_component_string(item):
                name = item.get("name") or item.get("component") or item.get("type") or "component"
                ports = item.get("ports") or item.get("port") or item.get("io")
                specs_pairs = [
                    f"{key}: {value}"
                    for key, value in item.items()
                    if key not in {"name", "component", "type", "ports", "port", "io"}
                ]
                specs_str = ", ".join(specs_pairs)
                if specs_str and ports:
                    return f"{name}, specifications: {{{specs_str}}}, ports: {ports}"
                if specs_str:
                    return f"{name}, specifications: {{{specs_str}}}"
                if ports:
                    return f"{name}, ports: {ports}"
                return str(name)

            if any(isinstance(item, dict) for item in data["components_list"]):
                data["components_list"] = [
                    _dict_to_component_string(item) if isinstance(item, dict) else str(item)
                    for item in data["components_list"]
                ]
    except Exception:
        pass


def _extract_json_dict(text):
    """Extract a JSON object from model output and parse it."""
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        raw = match.group(0)
    raw = raw.replace("\n", " ").replace("\r", " ")
    raw = re.sub(r"\s+", " ", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raw = re.sub(r",\s*}", "}", raw)
        raw = re.sub(r",\s*]", "]", raw)
        data = json.loads(raw)
    _normalize_components_list(data)
    return data


def call_openai_compatible(prompt, sys_prompt="", model="", n_completion=1, api_key="", base_url=""):
    """Call an OpenAI-compatible chat completions API."""
    prompt = truncate_prompt(prompt)
    if not api_key:
        raise Exception("未找到可用的 API Key。")
    if not base_url:
        raise Exception("未配置 API Base URL。")
    if not model:
        raise Exception("模型名不能为空。")

    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"

    messages = []
    if sys_prompt:
        messages.append({"role": "system", "content": sys_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "top_p": 0.7,
        "stream": False,
        "n": n_completion,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    verify_ssl_env = os.getenv("LLM_VERIFY_SSL", "1").strip().lower()
    verify_ssl = verify_ssl_env not in {"0", "false", "no", "off"}

    response = requests.post(endpoint, headers=headers, json=payload, timeout=120, verify=verify_ssl)
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        details = response.text.strip()
        raise Exception(f"LLM API HTTP error: {error}. Response: {details}") from error

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise Exception(f"LLM API 返回中没有 choices: {data}")

    usage = data.get("usage", {}) or {}
    input_tokens = usage.get("prompt_tokens", 0) or len(tokenizer.encode(prompt + sys_prompt))
    if n_completion == 1:
        output_tokens = usage.get("completion_tokens", 0) or len(
            tokenizer.encode(choices[0].get("message", {}).get("content", ""))
        )
    else:
        output_tokens = usage.get("completion_tokens", 0) or sum(
            len(tokenizer.encode(choice.get("message", {}).get("content", ""))) for choice in choices
        )
    add_token_usage(input_tokens, output_tokens, is_cached=False)

    if n_completion == 1:
        return choices[0].get("message", {}).get("content", "")
    return [choice.get("message", {}).get("content", "") for choice in choices]


def call_model_api(prompt, sys_prompt="", model="", n_completion=1, api_key=None, base_url=None):
    """Call the configured LLM provider using generic runtime settings."""
    runtime = get_runtime_llm_config()
    model = (model or runtime["model"] or "").strip()
    api_key = (api_key or runtime["api_key"] or "").strip()
    base_url = (base_url or runtime["base_url"] or "").strip()

    if not api_key:
        raise Exception("未找到可用的 API Key。请在程序开头填写 API Key。")
    if not model:
        raise Exception("模型名不能为空。请在程序开头填写模型名。")
    if not base_url:
        raise Exception("未配置 API Base URL。请在程序开头填写 API Base URL。")

    return call_openai_compatible(
        prompt,
        sys_prompt=sys_prompt,
        model=model,
        n_completion=n_completion,
        api_key=api_key,
        base_url=base_url,
    )


def _call_model_with_pydantic(prompt, sys_prompt, pydantic_model, model):
    """Use the configured model for all structured-output calls."""
    model = (model or "").strip()
    if not model:
        raise Exception("模型名不能为空。")

    schema = {}
    try:
        schema = pydantic_model.model_json_schema()
    except Exception:
        pass

    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    required = schema.get("required", []) if isinstance(schema, dict) else []
    fields_desc = ", ".join(
        [
            f"{name}:{(props.get(name, {}).get('type', 'string'))}{' (required)' if name in required else ''}"
            for name in props.keys()
        ]
    ) or "遵循模型字段定义"

    enhanced_sys = (
        f"{sys_prompt}\n\n"
        f"请严格按照 JSON 输出，不要添加任何额外解释或代码块标记。\n"
        f"字段与类型：{fields_desc}.\n"
        f"确保输出能被 json.loads 直接解析。"
    )
    return pydantic_model(**_extract_json_dict(call_model_api(prompt, enhanced_sys, model=model, n_completion=1)))


def callgpt_pydantic(prompt, sys_prompt, pydantic_model, model=None):
    """Structured output helper backed by the configured model."""
    chosen_model = (model or "").strip() or get_runtime_llm_config().get("model", "")
    return _call_model_with_pydantic(prompt, sys_prompt, pydantic_model, chosen_model)


def parse_and_validate_list(string):
    """Parse and validate a list from a string."""
    try:
        cleaned_string = string.strip()
        if cleaned_string.startswith("```"):
            lines = cleaned_string.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_string = "\n".join(lines).strip()

        lines = cleaned_string.split("\n")
        if lines and lines[0].strip().lower() in ["python", "yaml", "json"]:
            lines = lines[1:]
            cleaned_string = "\n".join(lines).strip()

        parsed_list = ast.literal_eval(cleaned_string)
        if not isinstance(parsed_list, list):
            raise ValueError(f"Parsed result is not a list, got {type(parsed_list)}: {parsed_list}")
        if all(isinstance(item, int) for item in parsed_list):
            return parsed_list

        non_integers = [item for item in parsed_list if not isinstance(item, int)]
        raise ValueError(f"Not all elements in the list are integers. Non-integers: {non_integers}")
    except (ValueError, SyntaxError) as error:
        print(f"Error parsing list from string: {error}")
        print(f"Original string: {string}")
        return None


def call_llm(prompt, sys_prompt, llm_api_selection="glm-4-flash"):
    """Call the LLM API.

    Args:
        prompt: The prompt to send to the model.
        sys_prompt: The system prompt to send to the model.
        llm_api_selection: The model name to use for the completion.
    """
    try:
        if llm_api_selection and llm_api_selection.strip():
            return call_model_api(prompt, sys_prompt, llm_api_selection.strip())
        return call_model_api(prompt, sys_prompt, "")
    except Exception as e:
        # Demo mode fallback when all APIs fail
        print(f"API unavailable for call_llm, using demo mode. Error: {e}")
        return "Demo mode: API service is currently unavailable. Please configure a valid API key to use full features."

def llm_retrieve(query, contexts, llm_api_selection):
    """Retrieve the best matched photonic components based on the query.

    Args:
        query: the query to search for.
        contexts: a list of photonic components to search from.
        llm_api_selection: the API to use for the search.
    """
    desc_ = dict(enumerate(contexts))
    desc_json = json.dumps(desc_, indent=2)
    # print(desc_json)

    sys_prompt = f"""Instructions: You are a photonic chip layout developer.
    The following JSON contains all available {len(contexts)} photonic devices, including their description and properties.
    When your are asked about a photonic component, you can only look at items listed in this JSON
    to find the best matched item.
    One important property that needs to be matched is the number of input and output ports.
    We use this notion to specify number of ports: [input]x[output]. For example a 1x2 device has one input and two output ports.
    In your answer, do not explain details of the process.
    Do not preamble your answer with quotes or other strings.
    Only output a python list of integers, with the ID of item(s) you find suitable for the given input text.

    JSON: \n\n{desc_json}\n\n
    """

    r = call_llm(query, sys_prompt, llm_api_selection)

    _indices = parse_and_validate_list(r)

    # Handle case where parsing failed
    if _indices is None:
        print(f"Warning: Failed to parse LLM response as list. Raw response: {r}")
        return []

    # remove duplicate IDs:
    seen = set()
    indices = [x for x in _indices if not (x in seen or seen.add(x))]

    return indices


class MatchedComponents(BaseModel):
    """Pydantic model for matched components.

    Args:
        match_list: The list of matched component IDs.
        match_scores: The list of match scores.
        match_comment: The match comment.
    """

    match_list: list[int]
    match_scores: list[str]
    match_comment: str


def llm_search(query, contexts, model=None):
    """Search for the best matched photonic components based on the query.

    Args:
        query: the query to search for.
        contexts: a list of photonic components to search from.
        model: optional model name to use for the search.
    """
    desc_ = dict(enumerate(contexts))
    desc_json = json.dumps(desc_, indent=2)

    sys_prompt = f"""You are a photonic chip layout developer.
    You have access to {len(contexts)} photonic devices/components, provided in the JSON below.
    Your task is to find the best-matched component(s) based on the described functionality and port configuration.

    Key matching criteria:
    1. Often a component is described with many specifications and modifiers.
       Identify the main component and functionality and search for a match to that.
       (e.g. a coupler with 10 nm bandwidth and with s-bend; the coupler is the main component and not the s-bend).
    2. Functionality is the highest priority.
    3. Match optical port configuration (e.g., [input]x[output] such as 1x2) when possible.
    4. If no exact match exists, prioritize functionality, then select the closest port configuration.
    5. If multiple close matches are found, rank them by the number of ports first, then by functionality closeness.
    6. If the query is ambiguous (missing function or port count details), make reasonable assumptions and provide a note in 'match_comment'.
    7. If no match is found, output the nearest match. Never output an empty list.

    For each matched item, return a qualitative score:
    - exact: Exactly matches both functionality and port configuration.
    - partial: A partial match with some differences in functionality or port configuration.
    - poor: Weak match or significantly different.

    Output the following:
    - match_list: List of matched item IDs.
    - match_scores: Corresponding qualitative scores.

    JSON of available components:

    {desc_json}
    """

    r = callgpt_pydantic(query, sys_prompt, MatchedComponents, model=model)

    if len(r.match_list) != len(r.match_scores):
        print(
            "Error: match_list and match_scores have different lengths.... trying again"
        )
        print(r.match_list, r.match_scores)
        r = callgpt_pydantic(query, sys_prompt, MatchedComponents)

    # It is also important to match the functionality of the seeking component.
    # For example, when looking for a high-speed resonant modulator all these functionalities should be matched.
    # If ports is a match but functionalities is a partial match, output the ID of found items in python list: partial_match_list.

    # print('=======')
    # print(r.match_list)
    # print(r.match_scores)
    # print(r.comment_str)
    # print('=======')

    return r


def dot_add_edges(session):
    _prompt = f"""You are an assistant to a photonic engineer.
You have two input DOT graphs:
- Graph1 has the correct definition of nodes including their ports, but the edges are missing.
- Graph2 has the correct definition of edges, but the nodes definition is incomplete.

Follow these instructions:
- add the edges from Graph2 to Graph1
- add the port numbers to the edge definitions (e.g. C1:o3 -- C2:o2;). Do not label the edges.
- Do not change the node definitions (the labels and the ports) in Graph1.
- Port are labelled as o1, o2, o3 etc, and they are ordered counter-clockwise around the rectangle node.
  For example a 2x3 node has o1 (left-bottom), o2 (left-top), o3 (right-top), o4 (right-middle), o5 (right-bottom).
- It is important that the edges don't cross. You should reason about the spatial location of ports around the
  rectangular nodes and make sure the edges are not crossing. Add you're reasoning in the comment field.
- Each port can only take one edge.
- Define only one edge between any two nodes, counting all node ports, unless explicitly stated.
- Do not connect a node to itself, unless explicitly stated.
- If there is only one node with no connections output Graph1. 
- Do not under any circumstances add additional nodes.

Do not explain or provide reasoning; only output dot code for a single valid dot graph. Do not preamble with "```dot".

INPUT graph1:
{session['p300_dot_string_draft']}

INPUT graph2:
{session['p200_preschematic']}
"""

    dot_graph_with_edges = call_llm(_prompt, "no prompt", session["p100_llm_api_selection"])
    print(dot_graph_with_edges)
    dot_graph_with_edges = re.sub(r"//.*", "", dot_graph_with_edges)  # remove comments

    return dot_graph_with_edges

def dot_add_edges_errorfunc(session):
    _prompt = f"""You are an assistant to a photonic engineer.
You have three input DOT graphs:
- Graph1 has the correct definition of nodes including their ports, but the edges are missing.
- Graph2 has the correct definition of edges, but the nodes definition is incomplete.
- Graph3 has the correct definition of nodes but a definition of edges that failed a test for crossings.

Follow these instructions:
- add the edges from Graph2 to Graph1. 
- add the port numbers to the edge definitions (e.g. C1:o3 -- C2:o2;). Do not label the edges.
- Do not change the node definitions (the labels and the ports) in Graph1.
- Port are labelled as o1, o2, o3 etc, and they are ordered counter-clockwise around the rectangle node.
  For example a 2x3 node has o1 (left-bottom), o2 (left-top), o3 (right-top), o4 (right-middle), o5 (right-bottom).
- It is important that the edges don't cross. You should reason about the spatial location of ports around the
  rectangular nodes and make sure the edges are not crossing. Add you're reasoning in the comment field.
  Refer to Graph3, which is a failed attempt.
- Each port can only take one edge.
- Define only one edge between any two nodes, counting all node ports, unless explicitly stated.
- Do not connect a node to itself, unless explicitly stated.
- If there is only one node with no connections output Graph1
- Do not under any circumstances add new nodes.

Do not explain or provide reasoning; only output dot code for a single valid dot graph. Do not preamble with "```dot".

INPUT graph1:
{session['p300_dot_string_draft']}

INPUT graph2:
{session['p200_preschematic']}

INPUT graph3:
{session['p300_dot_string']}
"""

    dot_graph_with_edges = call_llm(_prompt, "no prompt", session["p100_llm_api_selection"])
    print(dot_graph_with_edges)
    dot_graph_with_edges = re.sub(r"//.*", "", dot_graph_with_edges)  # remove comments

    return dot_graph_with_edges


def dot_add_edges_templates(session):
    """Add edges to a DOT graph.

    Args:
        session: The session to add edges to.
    """
    _prompt = str(session["p300_circuit_dsl"]["edges"])

    _prompt += "\nDOT Graph:\n" + session["p300_dot_string"]

    yaml_edges = call_llm(
        _prompt, prompts["edges_yaml_to_dot"], session["p100_llm_api_selection"]
    )

    yaml_data = yaml.safe_load(yaml_edges)
    edges_list = yaml_data["edges"]

    dot_graph_lines = session["p300_dot_string"].strip().split("\n")
    closing_bracket_index = dot_graph_lines.index("}")

    # Insert the edges just before the closing bracket
    # Handle both list and string formats
    if isinstance(edges_list, list):
        for edge in edges_list:
            dot_graph_lines.insert(closing_bracket_index, "  " + edge)
    else:
        # Handle string format (backward compatibility)
        for edge in edges_list.strip().split("\n"):
            dot_graph_lines.insert(closing_bracket_index, "  " + edge)

    # Join the lines back into a single string
    dot_graph_with_edges = "\n".join(dot_graph_lines)

    return dot_graph_with_edges


def dot_verify(session):
    """Verify a DOT graph.

    Args:
        session: The session to verify.
    """
    dot_updated = call_llm(
        session.p300_dot_string, prompts["dot_verify"], session.p100_llm_api_selection
    )

    # dot_updated = dot_updated.strip("```dot")
    dot_updated = dot_updated.replace("```dot", "").strip()

    return dot_updated


def netlist_cleanup(yaml_string):
    """Clean up a YAML string.

    Args:
        yaml_string: The YAML string to clean up.
    """
    updated_netlist = call_llm(yaml_string, prompts["yaml_syntax_cleaner"])

    return updated_netlist


class PromptClass(BaseModel):
    """Pydantic model for prompt classification.

    Args:
        category_id: The category ID.
        response: The response.
    """

    category_id: int
    response: str


def intent_classification(input_prompt):
    """Classify the input prompt into one of the categories.

    Args:
        input_prompt: The input prompt to classify.
    """
    # 快速关键词检测：如果输入包含明显的光子组件关键词，直接返回 category 1
    component_keywords = [
        "grating", "coupler", "mmi", "mzi", "ring", "resonator", "waveguide", 
        "crossing", "splitter", "modulator", "heater", "phase", "bragg",
        "taper", "y-branch", "directional", "dc ", "mrr", "filter",
        "laser", "detector", "photodiode", "sensor", "multiplexer", "demultiplexer",
        "wdm", "transceiver", "receiver", "transmitter", "amplifier", "attenuator"
    ]
    input_lower = input_prompt.lower()
    if any(kw in input_lower for kw in component_keywords):
        # 输入包含光子组件关键词，直接分类为 category 1
        return PromptClass(
            category_id=1,
            response="Photonic component design request detected."
        )
    
    sys_prompt = """You are an assistant to a photonic engineer.
Your task is to classify the input text into one of these categories (category_id):
category 1: A description of one or many photonic components/devices potentially forming a circuit.
Or a prompt to design/layout a photonic circuit/GDS.
This includes ANY request mentioning specific photonic components like grating couplers, MMIs, ring resonators, waveguides, MZIs, modulators, etc.
category 2: A generic question about integrated photonic, or photonic devices/components. Or a prompt to run any type of photonic simulation.
category 3: Not relevant to integrated photonics.
    If the category is 2 or 3, provide a response to the effect: I am only able to help desiging and layouting integrated photonics circuits.
    IMPORTANT: Any request to design or describe a specific photonic component (like "a grating coupler", "an MMI", "a ring resonator") should ALWAYS be category 1.
    """

    try:
        r = callgpt_pydantic(input_prompt, sys_prompt, PromptClass)
        return r
    except Exception as e:
        # Demo/Fallback mode when API is unavailable
        print(f"API unavailable, using demo mode. Error: {e}")
        # Default to category 1 (photonic design) for any input
        return PromptClass(
            category_id=1,
            response="API服务暂时不可用，使用演示模式。您的输入将被处理为光子电路设计请求。"
        )


class InputClarity(BaseModel):
    """Pydantic model for input clarity.

    Args:
        input_clarity: The clarity of the input.
        explain_ambiguity: The explanation of the ambiguity.
    """

    input_clarity: bool
    explain_ambiguity: str


def verify_input_clarity(input_prompt):
    """Verify the clarity of the input prompt.

    Args:
        input_prompt: The input prompt to verify.
    """
    sys_prompt = """You are an assistant to a photonic engineer.
The input is a description of photonic component(s) to be used in a photonic circuit.

- Is it clear from the input what photonic component(s) are being described?
- It is not required that each components have a detail specification. But if there is a specification, is it clear to which component it belongs?
- This is relevant only if more than one component is mentioned:
  Is there at least a hint about how to lay the components out or connect them?
  A sufficient info might be a simple connect A to B, or put A and B in series, or in parallel, etc.
  An insufficient info might be completely or partially missing info about how to the arrangement between all or some components.

If the answer to ALL of these questions is YES, set input_clarity to True.
Otherwise, set input_clarity to False and provide a brief explanation of the ambiguity in explain_ambiguity."""

    try:
        r = callgpt_pydantic(input_prompt, sys_prompt, InputClarity)
        return r.model_dump()
    except Exception as e:
        # Demo mode fallback
        print(f"API unavailable for verify_input_clarity, using demo mode. Error: {e}")
        return {"input_clarity": True, "explain_ambiguity": "Demo mode: API unavailable"}


class InputEntities(BaseModel):
    """Pydantic model for input entities.

    Args:
        title: The title of the input (optional).
        components_list: The list of components in the input.
        circuit_instructions: The instructions for the circuit.
        brief_summary: The brief summary of the input.
    """

    title: str = ""
    components_list: list[str]
    circuit_instructions: str
    brief_summary: str


class DesignModeDecision(BaseModel):
    """Pydantic model for deciding whether a request targets one device or a routed circuit."""

    design_type: str
    confidence: float
    reason: str


def _fallback_design_mode(input_prompt, extracted_entities=None):
    """Heuristic fallback for design mode classification when the agent call fails."""
    extracted_entities = extracted_entities or {}
    components = extracted_entities.get("components_list", []) if isinstance(extracted_entities, dict) else []
    circuit_instructions = ""

    if isinstance(extracted_entities, dict):
        circuit_instructions = str(extracted_entities.get("circuit_instructions", "") or "").strip()

    normalized_components = [str(component).strip() for component in components if str(component).strip()]
    prompt_lower = str(input_prompt or "").lower()
    routing_cues = (
        "connect",
        "route",
        "routing",
        "cascade",
        "cascaded",
        "tree",
        "mesh",
        "network",
        "link",
        "interconnect",
        "to each other",
    )
    has_routing_cue = any(cue in prompt_lower for cue in routing_cues)

    if len(normalized_components) <= 1 and not circuit_instructions and not has_routing_cue:
        design_type = "single_component"
        reason = "Fallback heuristic: one component and no routing instructions."
    else:
        design_type = "circuit_routing"
        reason = "Fallback heuristic: multiple components or routing intent detected."

    return {
        "design_type": design_type,
        "confidence": 0.35,
        "reason": reason,
    }


def design_mode_agent(input_prompt, extracted_entities=None):
    """Use a dedicated agent prompt to decide whether the request is single-component or multi-component."""
    extracted_entities = extracted_entities or {}

    if prompts and "design_mode_agent" in prompts:
        sys_prompt = prompts["design_mode_agent"]
    else:
        sys_prompt = """You are a photonic workflow router.
        Decide whether the request should enter:
        1. \"single_component\": optimize or generate one standalone device.
        2. \"circuit_routing\": build or route multiple devices together.

        Output JSON with fields:
        - design_type: \"single_component\" or \"circuit_routing\"
        - confidence: float between 0 and 1
        - reason: one concise sentence
        """

    agent_input = {
        "user_prompt": input_prompt,
        "extracted_entities": extracted_entities,
    }

    try:
        result = callgpt_pydantic(
            json.dumps(agent_input, ensure_ascii=False, indent=2),
            sys_prompt,
            DesignModeDecision,
        ).model_dump()
        if result.get("design_type") not in {"single_component", "circuit_routing"}:
            raise ValueError(f"Invalid design_type from design_mode_agent: {result}")
        return result
    except Exception as e:
        print(f"API unavailable for design_mode_agent, using fallback mode. Error: {e}")
        return _fallback_design_mode(input_prompt, extracted_entities)


def entity_extraction(input_prompt, design_type=None):
    """Extract entities from the input prompt.

    Args:
        input_prompt: The input prompt to extract entities from.
        design_type: Optional workflow mode from the independent design mode agent.
    """
    # Use the extraction-only prompt. Keep backward compatibility with the old key.
    if prompts and 'entity_extraction' in prompts:
        sys_prompt = prompts['entity_extraction']
    elif prompts and 'entity_extraction_with_intent' in prompts:
        sys_prompt = prompts['entity_extraction_with_intent']
    else:
        # Fallback to hardcoded prompt if yaml is missing key
        sys_prompt = """You are an expert photonic circuit architect. 
        Your task is to analyze the user's input and extract technical specifications.

        Output a JSON object with the following fields:
        - title: concise design title
        - components_list: [list of component names found]
        - circuit_instructions: (string) description of connections if any
        - brief_summary: (string) summary of the request
        """

    if design_type in {"single_component", "circuit_routing"}:
        sys_prompt += (
            "\n\nWorkflow context (already decided by a separate routing agent): "
            f"{design_type}. Use this as context only. Do not output a design_type field."
        )

    # If the input is very long (paper processing), we might want to stick to the paper extraction logic
    # But for now, let's funnel everything through the intent-aware prompt as per instructions
    # or perhaps only for short queries? The user context implies this is for the chat interface.
    
    # Original paper logic for very long text might still be useful, 
    # but the instructions were to "Refactor intent detection to prompts.yaml".
    # We will use the new prompt.

    try:
        r = callgpt_pydantic(input_prompt, sys_prompt, InputEntities)
        return r.model_dump()
    except Exception as e:
        # Demo mode fallback
        print(f"API unavailable for entity_extraction, using demo mode. Error: {e}")
        return {
            "title": "Demo Component",
            "components_list": ["mzi"],
            "circuit_instructions": "Demo mode: API unavailable",
            "brief_summary": "Demo mode - please configure a valid API key"
        }


class PaperEntities1(BaseModel):
    """Pydantic model for paper entities.

    Args:
        topic_photonic: Whether the article is about integrated photonic circuits.
        single_article: Whether the article is a single academic article.
        components_list: The list of components in the article.
        circuit_complete: Whether the article contains enough information to describe a photonic circuit.
    """

    topic_photonic: bool
    single_article: bool
    components_list: list[str]
    circuit_complete: bool


def papers_entity_extraction(input_article):
    """Extract entities from the input article.

    Args:
        input_article: The input article to extract entities from.
    """
    sys_prompt = """You are an assistant for a photonic engineer.

topic_photonic: Determine if the article is about integrated photonic circuits.

single_article: Confirm if this is a single academic article (not a dissertation or a collection of papers).

components_list: If both topic_photonic and single_article are True, extract a list of on-chip photonic components.
Follow these guidelines:
- Exclude electronic components (e.g., oscilloscope, transimpedance amplifier, DAC, RF source)
  and off-chip components (e.g., fiber, free-space lenses/lasers, EDFA).
- For each component, include specifications and descriptions if available.
- Extract the number of optical input and output ports for each component, if specified. Do not infer port counts if not explicitly stated.
- Avoid parsing descriptive modifiers or specifications as separate components. 
- If multiple instances of the same component are mentioned, list each explicitly.
- If the article does not contain any on-chip photonic components, set this field to an empty list.

circuit_complete: Assess if there is enough information to describe how the listed components are
interconnected to form a complete photonic circuit.
    """

    r = callgpt_pydantic(input_article, sys_prompt, PaperEntities1)

    return r.model_dump()


def preschematic(pretemplate, llm_api_selection):
    """Generate a preschematic from the pretemplate.

    Args:
        pretemplate: The pretemplate to generate a preschematic from.
    """
    dot_ = call_llm(yaml.dump(pretemplate), prompts["dot_simple"], llm_api_selection)
    return dot_


try:
    with open(PATH.templates) as file:
        templates_dict = yaml.safe_load(file)
        templates_str = yaml.dump(templates_dict, default_flow_style=False)
except FileNotFoundError:
    print(f"No {PATH.templates} file found.")
    pass

templates_titles = {key: value["doc"]["title"] for key, value in templates_dict.items()}
templates_titles_str = yaml.dump(templates_titles, sort_keys=False)


def parse_user_specs(session):
    """Parse user specifications from the input text.

    Args:
        session: The session to parse specifications from.
    """
    sys_prompt = f"You are an assistant to a photonic circuit engineer.\
            Your task is to parse specifications from the input text according to the template.\
            This is the template: {templates_dict[session['p200_selected_template']]['properties']['specs']}.\
            This is the input text: {session['p200_user_specs']}.\
            You should parse the input text into the template and return that object as a parsable python dict with the original syntax.\
            If user input is not compatible with the template (for example if the list size, the datatype, or the range is not compatible) answer with \
            an error message explaining the issue e.g. {{'Error': 'Four wavelengths are required but only two are provided.'}}.\
            Do no add any additional text or preambles like quotes etc."

    parsed_user_specs = call_llm(
        session["p200_user_specs"], sys_prompt, session["p100_llm_api_selection"]
    )

    # Check if the LLM call returned an error or is None/empty
    if parsed_user_specs is None:
        return {"Error": "No response received from LLM API"}
    
    if not parsed_user_specs.strip():
        return {"Error": "Empty response received from LLM API"}
    
    if parsed_user_specs.startswith("Error:"):
        return {"Error": parsed_user_specs}

    # Clean up the response - remove any markdown formatting and language identifiers
    parsed_user_specs = parsed_user_specs.strip()
    
    # Remove markdown code blocks
    if parsed_user_specs.startswith('```'):
        lines = parsed_user_specs.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        parsed_user_specs = '\n'.join(lines).strip()
    
    # Remove language identifiers at the beginning (like "python", "yaml", etc.)
    lines = parsed_user_specs.split('\n')
    if lines and lines[0].strip().lower() in ['python', 'yaml', 'json']:
        lines = lines[1:]
        parsed_user_specs = '\n'.join(lines).strip()

    # Try to parse as YAML first, if that fails, try to parse as Python dict
    try:
        # Try YAML parsing first
        return yaml.safe_load(parsed_user_specs)
    except yaml.YAMLError as yaml_error:
        try:
            # If YAML fails, try to parse as Python dict using ast.literal_eval
            import ast
            return ast.literal_eval(parsed_user_specs)
        except (ValueError, SyntaxError) as eval_error:
            # If both fail, try to fix common issues and retry
            try:
                # Try to fix common Python dict formatting issues
                fixed_specs = parsed_user_specs.replace("'", '"')  # Replace single quotes with double quotes
                return yaml.safe_load(fixed_specs)
            except yaml.YAMLError:
                # If all parsing attempts fail, return the original string with an error indicator
                return {"Error": f"Failed to parse LLM response. YAML error: {yaml_error}. Eval error: {eval_error}. Raw response: {parsed_user_specs}"}


def apply_settings(session, llm_api_selection):
    """Apply settings to the circuit DSL.

    Args:
        session: The session to apply settings to.
    """
    y1 = yaml.dump(session.p200_pretemplate_copy["components_list"])
    y2 = yaml.dump(session["p300_circuit_dsl"]["nodes"])
    llm_input = f"INPUT DESCRIPTION: \n{y1} \n\nNETLIST: \n{y2}"
    
    # Prefer STRICT JSON output from LLM to avoid YAML pitfalls
    strict_sys = (
        (prompts.get("absorb_settings") if isinstance(prompts, dict) else "")
        + "\n\n务必严格遵守以下要求：\n"
        + "1) 只输出一个 JSON 对象（即 nodes 映射），不要任何解释、不要 Markdown 代码块围栏、不要前后缀。\n"
        + "2) JSON 顶层是一个对象，键为节点名（如 N1、N2），值为该节点的对象（包含 component/placement/ports 等字段）。\n"
        + "3) 不要输出 YAML、不要输出额外自然语言，确保 json.loads 能直接解析。\n"
    )

    txt = call_llm(llm_input, strict_sys, llm_api_selection)

    # Try parse as pure JSON first (most strict)
    def _extract_json_object(s: str):
        s = (s or "").strip()
        # Quick path
        try:
            return json.loads(s)
        except Exception:
            pass
        # Remove code fences if present
        if s.startswith("```"):
            lines = s.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()
            try:
                return json.loads(s)
            except Exception:
                pass
        # Brace matching to extract first valid JSON object
        start = s.find('{')
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(s)):
            ch = s[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    segment = s[start:i+1]
                    try:
                        return json.loads(segment)
                    except Exception:
                        break
        return None

    updated_y2 = _extract_json_object(txt)
    # If JSON path failed, fall back to previous YAML-based sanitization path
    if updated_y2 is None:
        updated_y2 = txt

    # Pre-process the YAML returned by the LLM to be more lenient and quote risky values
    # 1) Wrap unquoted 'comment' (and similar) values that may contain ':' into quotes
    if isinstance(updated_y2, dict):
        # Already parsed strict JSON
        text = None
    else:
        text = updated_y2 if isinstance(updated_y2, str) else str(updated_y2)

    # Remove markdown code fences if present
    if text and text.strip().startswith("```"):
        lines = [ln for ln in text.strip().splitlines()]
        # drop first and last fence lines if present
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)

    # Specific: quote obvious narrative fields that tend to include colons
    if text:
        for key_name in ["comment", "comments", "description", "desc", "notes", "note", "summary"]:
            pattern = rf'^(\s*{key_name}:\s*)(.+)$'
            text = re.sub(
                pattern,
                lambda m: m.group(1) + '"' + m.group(2).strip().replace('"', '\\"') + '"'
                if not (m.group(2).strip().startswith("'") or m.group(2).strip().startswith('"')) else m.group(0),
                text,
                flags=re.MULTILINE,
            )

    # Generic: if a mapping value on the same line contains ':' and is not a structured value, quote it
    def _quote_rhs_if_needed(match: re.Match) -> str:
        left, right = match.group(1), match.group(2).strip()
        if not right:
            return match.group(0)
        # don't touch already quoted or structured values
        if right.startswith('{') or right.startswith('[') or right.startswith('|') or right.startswith('>'):
            return match.group(0)
        if (right.startswith('"') and right.endswith('"')) or (right.startswith("'") and right.endswith("'")):
            return match.group(0)
        # if colon exists in a plain scalar, quote it
        if ':' in right:
            safe = right.replace('"', '\\"')
            return f"{left}\"{safe}\""
        return match.group(0)

    if text:
        text = re.sub(r'^(\s*[A-Za-z0-9_\-]+:\s*)(.+)$', _quote_rhs_if_needed, text, flags=re.MULTILINE)

    # Now try to load sanitized YAML / or repair JSON-like content
    if not isinstance(updated_y2, dict):
        parsed = None
        if text:
            # First attempt: direct YAML
            try:
                parsed = yaml.safe_load(text)
            except Exception:
                parsed = None

            if parsed is None:
                # Second attempt: convert narrative fields to block scalars and try YAML again
                def to_block_scalar(match: re.Match) -> str:
                    indent = match.group(1)
                    key = match.group(2)
                    rhs = match.group(3).strip()
                    # strip surrounding quotes if present
                    if (rhs.startswith('"') and rhs.endswith('"')) or (rhs.startswith("'") and rhs.endswith("'")):
                        rhs = rhs[1:-1]
                    # unescape
                    rhs = rhs.replace('\\"', '"')
                    block_lines = [f"{indent}{key}: |", f"{indent}  {rhs}"]
                    return "\n".join(block_lines)

                block_pattern = re.compile(r"^(\s*)(comment|comments|description|desc|notes|note|summary):\s*(.+)$", re.MULTILINE)
                text_block = re.sub(block_pattern, to_block_scalar, text)
                try:
                    parsed = yaml.safe_load(text_block)
                except Exception:
                    parsed = None

            if parsed is None:
                # Third attempt: repair common missing commas in JSON-like maps
                # Insert a comma between successive key-value pairs like: "k1": v1 \n "k2": v2
                text_jsonish = re.sub(r'("\s*:\s*[^,\n\{\}\[\]]+)\s*\n\s*(")', r'\1,\n\2', text)
                # Try to extract and parse JSON object after repair
                obj = _extract_json_object(text_jsonish)
                if isinstance(obj, dict):
                    parsed = obj

            if parsed is None:
                # Final attempt: ast.literal_eval on a Python-like dict
                try:
                    import ast as _ast
                    parsed = _ast.literal_eval(text)
                except Exception:
                    parsed = None

        updated_y2 = parsed if isinstance(parsed, dict) else None
        if updated_y2 is None:
            # As a last resort, keep prior nodes unchanged to avoid crashing UI
            return session["p300_circuit_dsl"]
    # Ensure result is a mapping and strip stray comment fields
    if not isinstance(updated_y2, dict):
        raise ValueError("apply_settings: LLM 返回的 YAML 不是映射类型，无法更新 nodes")
    if "comment" in updated_y2:
        try:
            del updated_y2["comment"]
        except Exception:
            pass
    for k, v in list(updated_y2.items()):
        if isinstance(v, dict) and "comment" in v:
            try:
                del updated_y2[k]["comment"]
            except Exception:
                pass

    session["p300_circuit_dsl"]["nodes"] = updated_y2

    # updated_netlist = verifiers.verify_and_filter_netlist(updated_netlist)
    return session["p300_circuit_dsl"]
