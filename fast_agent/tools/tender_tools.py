from fast_agent.llm import llm

def generate_tender_outline(theme: str, content_requirements: str) -> str:
    """根据主题和内容要求生成标书大纲
    Args:
        theme: 招标项目的主题
        content_requirements: 内容生成要求
    Returns:
        str: 生成的标书大纲
    """
    response = llm.generate(
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的标书专家，你能详细设计招标文件的大纲"
            },
            {
                "role": "user",
                "content": f"根据主题和内容要求生成标书大纲，主题: {theme}, 内容要求: {content_requirements}"
            }
        ],
        stream=False)
    return response.choices[0].message.content

def update_tender_outline(outline: str, content_requirements: str) -> str:
    """优化标书大纲，根据内容要求优化标书大纲
    Args:
        outline: 标书大纲
        content_requirements: 内容生成要求
    Returns:
        str: 更新后的标书大纲
    """
    response = llm.generate(
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的标书专家，你能根据内容要求优化标书大纲"
            },
            {
                "role": "user",
                "content": f"根据内容要求优化标书大纲，标书大纲: {outline}, 内容要求: {content_requirements}"
            }
        ],
        stream=False)
    return response.choices[0].message.content

