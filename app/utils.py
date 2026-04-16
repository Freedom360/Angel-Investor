import time
import functools

import re

def retry_on_demand_error(max_retries=4, initial_delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e)
                    if "503" in error_msg or "429" in error_msg:
                        if attempt == max_retries - 1:
                            raise e
                            
                        match = re.search(r'Please retry in ([\d\.]+)s', error_msg)
                        if match:
                            delay = float(match.group(1)) + 2.0
                        else:
                            delay = initial_delay * (2 ** attempt)
                            
                        print(f"Server busy (503/429). Retrying in {delay} seconds...")
                        import streamlit as st
                        try: # Try to warn in UI if possible
                            st.toast(f"Rate limited. Retrying in {int(delay)}s...")
                        except:
                            pass
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator
