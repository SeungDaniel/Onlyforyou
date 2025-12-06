import re
from datetime import time

def parse_korean_time(text: str) -> time:
    """
    Parses a Korean time string into a datetime.time object.
    Examples:
    - "오전 9시" -> 09:00
    - "오후 2시 30분" -> 14:30
    - "밤 10시반" -> 22:30
    - "14:00" -> 14:00
    """
    text = text.replace(" ", "")
    
    # Check for HH:MM format first
    match_digital = re.match(r"(\d{1,2}):(\d{2})", text)
    if match_digital:
        hour, minute = map(int, match_digital.groups())
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)

    # Korean format parsing
    is_pm = False
    if any(x in text for x in ["오후", "저녁", "밤"]):
        is_pm = True
    
    # Extract numbers
    numbers = re.findall(r"\d+", text)
    if not numbers:
        return None
    
    hour = int(numbers[0])
    minute = 0
    
    if len(numbers) > 1:
        minute = int(numbers[1])
    elif "반" in text:
        minute = 30
        
    # Adjust for PM
    if is_pm and hour < 12:
        hour += 12
    # Adjust for special case "12시" (noon vs midnight is context dependent, but usually 12pm is noon)
    # If user says "오전 12시" -> 00:00, "오후 12시" -> 12:00
    if "오전" in text and hour == 12:
        hour = 0
        
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return time(hour, minute)
        
    return None
