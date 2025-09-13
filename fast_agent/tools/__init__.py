from smolagents import tool
from .math_tools import (
    add, sub, multiply, divide, power, square_root, factorial, 
    absolute_value, modulo, gcd, lcm, sin, cos, tan, 
    degrees_to_radians, radians_to_degrees, natural_log, 
    log_base_10, log_base_n, mean, median, mode, variance, 
    standard_deviation, fibonacci, is_prime, prime_factors, 
    combination, permutation
)


tools_list = [
    tool(add),
    tool(sub),
    tool(multiply),
    tool(divide),
    tool(power),
    tool(square_root),
    tool(factorial),
    tool(absolute_value),
    tool(modulo),
    tool(gcd),
    tool(lcm),
    tool(sin),
    tool(cos),
    tool(tan),
    tool(degrees_to_radians),
    tool(radians_to_degrees),
    tool(natural_log),
    tool(log_base_10),
    tool(log_base_n),
    tool(mean),
    tool(median),
    tool(mode),
    tool(variance),
    tool(standard_deviation),
    tool(fibonacci),
    tool(is_prime),
    tool(prime_factors),
    tool(combination),
    tool(permutation)
]
