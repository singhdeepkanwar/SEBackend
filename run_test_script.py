import os
import sys
from django.core.management import call_command
from io import StringIO

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 
import django
django.setup()

def run_test():
    out = StringIO()
    sys.stdout = out
    sys.stderr = out
    
    try:
        call_command('test', verbosity=2)
    except Exception as e:
        print(f"EXCEPTION: {e}")
    finally:
        with open('test_result.txt', 'w', encoding='utf-8') as f:
            f.write(out.getvalue())

if __name__ == '__main__':
    run_test()
