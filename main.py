import psutil
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Path to your credentials JSON file downloaded from Google Cloud Console
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/krishnavamshi/Downloads/scenic-alcove-417811-92e46a756544.json', scope)

# Authorize the client
client = gspread.authorize(creds)

# Replace 'YOUR_SPREADSHEET_URL' with the provided Google Sheets link
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1M6UZcXTdvY4bzUkfG3-KIkwgNPX8WKAS8eESsqZUXvU/edit?usp=sharing'

# Open the Google Sheets spreadsheet by its URL
sheet = client.open_by_url(spreadsheet_url).sheet1

def check_and_create_headers():
    # Check if the first row is empty
    first_row = sheet.row_values(1)
    if not any(first_row):
        headers = ["Timestamp", "CPU Usage", "Memory Usage", "Top CPU Processes", "Top Memory Processes"]
        sheet.insert_row(headers, index=1)

# Check and create headers if needed
check_and_create_headers()

def get_system_info():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    cpu_processes = get_top_processes_by_cpu()
    memory_processes = get_top_processes_by_memory()
    return cpu_percent, memory_percent, cpu_processes, memory_processes

def get_top_processes_by_cpu():
    processes = sorted(psutil.process_iter(attrs=['name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)
    return [proc.info['name'] for proc in processes[:2]]

def get_top_processes_by_memory():
    processes = sorted(psutil.process_iter(attrs=['name', 'memory_percent']), key=lambda x: x.info['memory_percent'], reverse=True)
    return [proc.info['name'] for proc in processes[:2]]

def write_to_sheet(cpu_percent, memory_percent, cpu_processes, memory_processes):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, f"{cpu_percent:.2f}%", f"{memory_percent:.2f}%", ', '.join(cpu_processes), ', '.join(memory_processes)])

def main(interval):
    while True:
        cpu_percent, memory_percent, cpu_processes, memory_processes = get_system_info()
        write_to_sheet(cpu_percent, memory_percent, cpu_processes, memory_processes)
        time.sleep(interval)

if __name__ == "__main__":
    interval = 60  # Time interval in seconds
    main(interval)
