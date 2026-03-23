import sys
from task_manager import TaskFlowApp
from datetime import datetime

app = TaskFlowApp()
app.ent_task.insert(0, "Test task 1")
app.ent_date.insert(0, "")
app._filter = "today"
app._add()

filtered = app._get_filtered()
print(f"Filtered Today tasks: {len(filtered)}")

app.ent_task.insert(0, "Test task 2")
# Add tomorrow's date
tomorrow = datetime.now().replace(day=datetime.now().day + 1)
app.ent_date.insert(0, tomorrow.strftime("%d/%m") )
app._add()

app._filter = "upcoming"
filtered2 = app._get_filtered()
print(f"Filtered Upcoming tasks: {len(filtered2)}")

app.destroy()
sys.exit(0)
