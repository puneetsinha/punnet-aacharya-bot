#!/usr/bin/env python
"""
Log Viewer Utility for Punnet Aacharya Bot
This utility helps monitor and analyze logs in real-time
"""

import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path

def view_logs(log_file=None, follow=False, filter_level=None, filter_function=None):
    """View logs with various filtering options"""
    
    # Find the most recent log file if not specified
    if not log_file:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print("❌ No logs directory found!")
            return
        
        log_files = list(logs_dir.glob("punnet_aacharya_*.log"))
        if not log_files:
            print("❌ No log files found!")
            return
        
        # Get the most recent log file
        log_file = max(log_files, key=lambda x: x.stat().st_mtime)
        print(f"📄 Using log file: {log_file}")
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return
    
    print(f"🔍 Viewing logs from: {log_file}")
    print("=" * 80)
    
    try:
        with open(log_file, 'r') as f:
            if follow:
                print("🔄 Following logs in real-time (Ctrl+C to stop)...")
                print("-" * 80)
                
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        if should_display_line(line, filter_level, filter_function):
                            print(line.rstrip())
                    else:
                        time.sleep(0.1)
            else:
                # Read all lines
                lines = f.readlines()
                displayed_count = 0
                
                for line in lines:
                    if should_display_line(line, filter_level, filter_function):
                        print(line.rstrip())
                        displayed_count += 1
                
                print(f"\n📊 Displayed {displayed_count} lines out of {len(lines)} total lines")
                
    except KeyboardInterrupt:
        print("\n⏹️  Stopped following logs")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def should_display_line(line, filter_level=None, filter_function=None):
    """Check if line should be displayed based on filters"""
    
    # Level filter
    if filter_level:
        if filter_level.upper() not in line.upper():
            return False
    
    # Function filter
    if filter_function:
        if filter_function.lower() not in line.lower():
            return False
    
    return True

def analyze_logs(log_file=None):
    """Analyze logs for patterns and statistics"""
    
    if not log_file:
        logs_dir = Path("logs")
        log_files = list(logs_dir.glob("punnet_aacharya_*.log"))
        if not log_files:
            print("❌ No log files found for analysis!")
            return
        log_file = max(log_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📊 Analyzing logs from: {log_file}")
    print("=" * 80)
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Statistics
        total_lines = len(lines)
        error_lines = [l for l in lines if 'ERROR' in l]
        warning_lines = [l for l in lines if 'WARNING' in l]
        info_lines = [l for l in lines if 'INFO' in l]
        debug_lines = [l for l in lines if 'DEBUG' in l]
        
        # Function call analysis
        function_calls = {}
        for line in lines:
            # Extract function name from log format
            match = re.search(r'(\w+):\d+ -', line)
            if match:
                func_name = match.group(1)
                function_calls[func_name] = function_calls.get(func_name, 0) + 1
        
        # User interaction analysis
        user_interactions = [l for l in lines if 'user' in l.lower()]
        
        # Gemini AI interactions
        gemini_calls = [l for l in lines if 'gemini' in l.lower()]
        
        # Print analysis
        print(f"📈 Total log lines: {total_lines}")
        print(f"❌ Error lines: {len(error_lines)}")
        print(f"⚠️  Warning lines: {len(warning_lines)}")
        print(f"ℹ️  Info lines: {len(info_lines)}")
        print(f"🔍 Debug lines: {len(debug_lines)}")
        print()
        
        print("🔧 Function Call Analysis:")
        for func, count in sorted(function_calls.items(), key=lambda x: x[1], reverse=True):
            print(f"  {func}: {count} calls")
        print()
        
        print("👥 User Interactions:")
        print(f"  Total user interactions: {len(user_interactions)}")
        print()
        
        print("🤖 Gemini AI Interactions:")
        print(f"  Total Gemini calls: {len(gemini_calls)}")
        print()
        
        # Show recent errors if any
        if error_lines:
            print("❌ Recent Errors:")
            for error in error_lines[-5:]:  # Last 5 errors
                print(f"  {error.strip()}")
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")

def show_help():
    """Show help information"""
    print("""
🔍 Punnet Aacharya Log Viewer

Usage:
  python log_viewer.py [command] [options]

Commands:
  view [log_file]           - View logs (default: most recent)
  follow [log_file]         - Follow logs in real-time
  analyze [log_file]        - Analyze log statistics
  help                     - Show this help

Options:
  --level=ERROR            - Filter by log level
  --function=calculate     - Filter by function name

Examples:
  python log_viewer.py view
  python log_viewer.py follow
  python log_viewer.py analyze
  python log_viewer.py view --level=ERROR
  python log_viewer.py view --function=generate_birth_chart
""")

def main():
    """Main function"""
    if len(sys.argv) < 2 or sys.argv[1] in ['help', '--help', '-h']:
        show_help()
        return
    
    command = sys.argv[1]
    log_file = None
    filter_level = None
    filter_function = None
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg.startswith('--level='):
            filter_level = arg.split('=')[1]
        elif arg.startswith('--function='):
            filter_function = arg.split('=')[1]
        elif not arg.startswith('--'):
            log_file = arg
    
    if command == 'view':
        view_logs(log_file, follow=False, filter_level=filter_level, filter_function=filter_function)
    elif command == 'follow':
        view_logs(log_file, follow=True, filter_level=filter_level, filter_function=filter_function)
    elif command == 'analyze':
        analyze_logs(log_file)
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main() 