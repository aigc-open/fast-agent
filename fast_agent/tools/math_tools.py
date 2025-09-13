import math
from typing import Union, List

def add(a: int, b: int) -> int:
    """两个数求和
    Args:
        a: The first number
        b: The second number
    Returns:
        The sum of the two numbers
    """
    return a + b

def sub(a: int, b: int) -> int:
    """两个数求差
    Args:
        a: The first number
        b: The second number
    Returns:
        The difference of the two numbers
    """
    return a - b

def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """两个数相乘
    Args:
        a: The first number
        b: The second number
    Returns:
        The product of the two numbers
    """
    return a * b

def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """两个数相除
    Args:
        a: The dividend
        b: The divisor
    Returns:
        The quotient of the two numbers
    Raises:
        ValueError: If divisor is zero
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
    """计算幂运算
    Args:
        base: The base number
        exponent: The exponent
    Returns:
        The result of base raised to the power of exponent
    """
    return base ** exponent

def square_root(x: Union[int, float]) -> float:
    """计算平方根
    Args:
        x: The number to find square root of
    Returns:
        The square root of x
    Raises:
        ValueError: If x is negative
    """
    if x < 0:
        raise ValueError("不能计算负数的平方根")
    return math.sqrt(x)

def factorial(n: int) -> int:
    """计算阶乘
    Args:
        n: The number to calculate factorial of
    Returns:
        The factorial of n
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("不能计算负数的阶乘")
    if n == 0 or n == 1:
        return 1
    return math.factorial(n)

def absolute_value(x: Union[int, float]) -> Union[int, float]:
    """计算绝对值
    Args:
        x: The number
    Returns:
        The absolute value of x
    """
    return abs(x)

def modulo(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """计算取模运算
    Args:
        a: The dividend
        b: The divisor
    Returns:
        The remainder of a divided by b
    Raises:
        ValueError: If divisor is zero
    """
    if b == 0:
        raise ValueError("除数不能为零")
    return a % b

def gcd(a: int, b: int) -> int:
    """计算最大公约数
    Args:
        a: The first number
        b: The second number
    Returns:
        The greatest common divisor of a and b
    """
    return math.gcd(a, b)

def lcm(a: int, b: int) -> int:
    """计算最小公倍数
    Args:
        a: The first number
        b: The second number
    Returns:
        The least common multiple of a and b
    """
    return abs(a * b) // math.gcd(a, b)

# 三角函数
def sin(x: Union[int, float]) -> float:
    """计算正弦值
    Args:
        x: The angle in radians
    Returns:
        The sine of x
    """
    return math.sin(x)

def cos(x: Union[int, float]) -> float:
    """计算余弦值
    Args:
        x: The angle in radians
    Returns:
        The cosine of x
    """
    return math.cos(x)

def tan(x: Union[int, float]) -> float:
    """计算正切值
    Args:
        x: The angle in radians
    Returns:
        The tangent of x
    """
    return math.tan(x)

def degrees_to_radians(degrees: Union[int, float]) -> float:
    """角度转弧度
    Args:
        degrees: The angle in degrees
    Returns:
        The angle in radians
    """
    return math.radians(degrees)

def radians_to_degrees(radians: Union[int, float]) -> float:
    """弧度转角度
    Args:
        radians: The angle in radians
    Returns:
        The angle in degrees
    """
    return math.degrees(radians)

# 对数函数
def natural_log(x: Union[int, float]) -> float:
    """计算自然对数
    Args:
        x: The number (must be positive)
    Returns:
        The natural logarithm of x
    Raises:
        ValueError: If x is not positive
    """
    if x <= 0:
        raise ValueError("对数的真数必须为正数")
    return math.log(x)

def log_base_10(x: Union[int, float]) -> float:
    """计算以10为底的对数
    Args:
        x: The number (must be positive)
    Returns:
        The base-10 logarithm of x
    Raises:
        ValueError: If x is not positive
    """
    if x <= 0:
        raise ValueError("对数的真数必须为正数")
    return math.log10(x)

def log_base_n(x: Union[int, float], base: Union[int, float]) -> float:
    """计算以指定底数的对数
    Args:
        x: The number (must be positive)
        base: The base (must be positive and not equal to 1)
    Returns:
        The logarithm of x with the specified base
    Raises:
        ValueError: If x or base is not valid
    """
    if x <= 0:
        raise ValueError("对数的真数必须为正数")
    if base <= 0 or base == 1:
        raise ValueError("对数的底数必须为正数且不等于1")
    return math.log(x, base)

# 统计函数
def mean(numbers: List[Union[int, float]]) -> float:
    """计算平均值
    Args:
        numbers: A list of numbers
    Returns:
        The arithmetic mean of the numbers
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("列表不能为空")
    return sum(numbers) / len(numbers)

def median(numbers: List[Union[int, float]]) -> Union[int, float]:
    """计算中位数
    Args:
        numbers: A list of numbers
    Returns:
        The median of the numbers
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("列表不能为空")
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]

def mode(numbers: List[Union[int, float]]) -> Union[int, float]:
    """计算众数
    Args:
        numbers: A list of numbers
    Returns:
        The mode of the numbers
    Raises:
        ValueError: If the list is empty or has no mode
    """
    if not numbers:
        raise ValueError("列表不能为空")
    
    from collections import Counter
    counter = Counter(numbers)
    max_count = max(counter.values())
    modes = [num for num, count in counter.items() if count == max_count]
    
    if len(modes) == len(numbers):
        raise ValueError("没有众数")
    
    return modes[0] if len(modes) == 1 else modes

def variance(numbers: List[Union[int, float]]) -> float:
    """计算方差
    Args:
        numbers: A list of numbers
    Returns:
        The variance of the numbers
    Raises:
        ValueError: If the list is empty or has only one element
    """
    if len(numbers) < 2:
        raise ValueError("至少需要两个数据点来计算方差")
    
    avg = mean(numbers)
    return sum((x - avg) ** 2 for x in numbers) / (len(numbers) - 1)

def standard_deviation(numbers: List[Union[int, float]]) -> float:
    """计算标准差
    Args:
        numbers: A list of numbers
    Returns:
        The standard deviation of the numbers
    Raises:
        ValueError: If the list is empty or has only one element
    """
    return math.sqrt(variance(numbers))

# 其他高级函数
def fibonacci(n: int) -> int:
    """计算斐波那契数列第n项
    Args:
        n: The position in the sequence (0-indexed)
    Returns:
        The nth Fibonacci number
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n必须为非负整数")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def is_prime(n: int) -> bool:
    """判断是否为质数
    Args:
        n: The number to check
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def prime_factors(n: int) -> List[int]:
    """计算质因数分解
    Args:
        n: The number to factorize
    Returns:
        A list of prime factors
    Raises:
        ValueError: If n is less than 2
    """
    if n < 2:
        raise ValueError("n必须大于等于2")
    
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def combination(n: int, r: int) -> int:
    """计算组合数C(n,r)
    Args:
        n: Total number of items
        r: Number of items to choose
    Returns:
        The number of combinations
    Raises:
        ValueError: If n or r is negative, or r > n
    """
    if n < 0 or r < 0:
        raise ValueError("n和r必须为非负整数")
    if r > n:
        raise ValueError("r不能大于n")
    return math.comb(n, r)

def permutation(n: int, r: int) -> int:
    """计算排列数P(n,r)
    Args:
        n: Total number of items
        r: Number of items to arrange
    Returns:
        The number of permutations
    Raises:
        ValueError: If n or r is negative, or r > n
    """
    if n < 0 or r < 0:
        raise ValueError("n和r必须为非负整数")
    if r > n:
        raise ValueError("r不能大于n")
    return math.perm(n, r)