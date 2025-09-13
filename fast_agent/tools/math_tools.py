from smolagents import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers
    Args:
        a: The first number
        b: The second number
    Returns:
        The sum of the two numbers
    """
    print(f"Adding {a} and {b}")

    return a + b

