def is_palindrome(s):
    """
    Check if a given string is a palindrome.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is a palindrome, False otherwise.
    """
    s = ''.join(filter(str.isalnum, s)).lower()  # Remove non-alphanumeric characters and convert to lowercase
    return s == s[::-1]

def factorial(n):
    """
    Calculate the factorial of a given number.

    Args:
        n (int): The number to calculate the factorial for.

    Returns:
        int: The factorial of the number.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def flatten_list(nested_list):
    """
    Flatten a nested list into a single list.

    Args:
        nested_list (list): A list that may contain other lists.

    Returns:
        list: A flattened list.
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened
