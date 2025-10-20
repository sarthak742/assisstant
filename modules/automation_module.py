import os
import json
import logging
import time
import threading
from datetime import datetime, timedelta

class AutomationModule:
    """
    Module for handling task scheduling, repetitive task automation,
    custom script execution, and data retrieval/processing.
    """
    
    def __init__(self, memory_manager, system_control):
        """Initialize the Automation & Productivity Module."""
        self.logger = logging.getLogger("jarvis.automation")
        self.memory_manager = memory_manager
        self.system_control = system_control
        self.scheduled_tasks = {}
        self.running_tasks = {}
        self.automation_settings = self._load_automation_settings()
        self.scheduler_thread = None
        self.scheduler_running = False
        
    def _load_automation_settings(self):
        """Load automation settings from memory manager"""
        try:
            settings = self.memory_manager.get_preference("automation_settings")
            if not settings:
                # Default automation settings
                settings = {
                    "scripts_directory": os.path.join(os.getcwd(), "scripts"),
                    "max_concurrent_tasks": 5,
                    "default_retry_count": 3,
                    "task_history_limit": 100
                }
                
                # Create scripts directory if it doesn't exist
                if not os.path.exists(settings["scripts_directory"]):
                    os.makedirs(settings["scripts_directory"])
                    
                self.memory_manager.store_preference("automation_settings", settings)
            return settings
        except Exception as e:
            self.logger.error(f"Error loading automation settings: {str(e)}")
            return {}
    
    def start_scheduler(self):
        """Start the task scheduler in a background thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return "Scheduler is already running"
            
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        return "Task scheduler started"
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            return "Scheduler is not running"
            
        self.scheduler_running = False
        self.scheduler_thread.join(timeout=2.0)
        return "Task scheduler stopped"
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.scheduler_running:
            self._check_scheduled_tasks()
            time.sleep(1)
    
    def _check_scheduled_tasks(self):
        """Check for tasks that need to be executed"""
        now = datetime.now()
        for task_id, task in list(self.scheduled_tasks.items()):
            if task["status"] == "scheduled":
                next_run = datetime.fromisoformat(task["next_run"])
                if now >= next_run:
                    # Execute the task
                    threading.Thread(target=self._execute_task, args=(task_id,)).start()
    
    def schedule_task(self, task_name, command, schedule_type, schedule_time, repeat=False):
        """
        Schedule a task to run at a specific time.
        
        Args:
            task_name: Name of the task
            command: Command to execute
            schedule_type: Type of schedule (once, daily, weekly, monthly)
            schedule_time: Time to run the task (format depends on schedule_type)
            repeat: Whether to repeat the task
            
        Returns:
            Success message
        """
        try:
            # Create task object
            task = {
                "name": task_name,
                "command": command,
                "schedule_type": schedule_type,
                "schedule_time": schedule_time,
                "repeat": repeat,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": None,
                "status": "scheduled"
            }
            
            # Calculate next run time
            next_run = self._calculate_next_run(schedule_type, schedule_time)
            if not next_run:
                return f"Invalid schedule parameters for task: {task_name}"
                
            task["next_run"] = next_run.isoformat()
            
            # Add to scheduled tasks
            task_id = f"{task_name}_{int(time.time())}"
            self.scheduled_tasks[task_id] = task
            
            # Save scheduled tasks to memory
            self._save_scheduled_tasks()
            
            return f"Task '{task_name}' scheduled successfully. Next run: {next_run}"
        except Exception as e:
            self.logger.error(f"Error scheduling task: {str(e)}")
            return f"Failed to schedule task. Error: {str(e)}"
    
    def _calculate_next_run(self, schedule_type, schedule_time):
        """Calculate the next run time for a scheduled task"""
        try:
            now = datetime.now()
            
            if schedule_type == "once":
                # Format: "YYYY-MM-DD HH:MM"
                return datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
                
            elif schedule_type == "daily":
                # Format: "HH:MM"
                hour, minute = map(int, schedule_time.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
                
            elif schedule_type == "weekly":
                # Format: "DAY HH:MM" (e.g., "Monday 09:00")
                day_name, time_str = schedule_time.split()
                hour, minute = map(int, time_str.split(":"))
                
                days = {"monday": 0, "tuesday": 1, "wednesday": 2, 
                       "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
                target_day = days.get(day_name.lower())
                
                if target_day is None:
                    return None
                    
                current_day = now.weekday()
                days_ahead = target_day - current_day
                if days_ahead <= 0:
                    days_ahead += 7
                    
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return next_run
                
            elif schedule_type == "monthly":
                # Format: "DAY HH:MM" (e.g., "15 09:00" for 15th day of month)
                day_str, time_str = schedule_time.split()
                day = int(day_str)
                hour, minute = map(int, time_str.split(":"))
                
                next_run = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
                
                # Move to next month if current day is past the target day
                if now.day > day or (now.day == day and now.time() >= next_run.time()):
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
                
                # Set the correct day, handling month length issues
                month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if next_run.year % 4 == 0 and (next_run.year % 100 != 0 or next_run.year % 400 == 0):
                    month_days[1] = 29
                    
                next_run = next_run.replace(day=min(day, month_days[next_run.month - 1]))
                return next_run
                
            return None
        except Exception as e:
            self.logger.error(f"Error calculating next run time: {str(e)}")
            return None
    
    def _execute_task(self, task_id):
        """Execute a scheduled task"""
        if task_id not in self.scheduled_tasks:
            return
            
        task = self.scheduled_tasks[task_id]
        task["last_run"] = datetime.now().isoformat()
        task["status"] = "running"
        
        try:
            # Execute the command
            command = task["command"]
            
            # Check if it's a system command or a script
            if command.startswith("script:"):
                script_name = command[7:]
                result = self.run_script(script_name)
            else:
                result = self.system_control.execute_command(command)
                
            # Update task status
            task["status"] = "completed"
            task["result"] = result
            
            # Calculate next run time if repeating
            if task["repeat"]:
                next_run = self._calculate_next_run(task["schedule_type"], task["schedule_time"])
                if next_run:
                    task["next_run"] = next_run.isoformat()
                    task["status"] = "scheduled"
            else:
                # Remove non-repeating tasks after execution
                self.scheduled_tasks.pop(task_id, None)
                
            # Save scheduled tasks to memory
            self._save_scheduled_tasks()
            
            # Log task execution
            self.logger.info(f"Task executed: {task['name']}")
            
            return result
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
            self.logger.error(f"Error executing task {task['name']}: {str(e)}")
            self._save_scheduled_tasks()
            return None
    
    def _save_scheduled_tasks(self):
        """Save scheduled tasks to memory manager"""
        try:
            self.memory_manager.store_preference("scheduled_tasks", self.scheduled_tasks)
        except Exception as e:
            self.logger.error(f"Error saving scheduled tasks: {str(e)}")
    
    def get_scheduled_tasks(self):
        """
        Get all scheduled tasks.
        
        Returns:
            Dictionary of scheduled tasks
        """
        return self.scheduled_tasks
    
    def cancel_task(self, task_id):
        """
        Cancel a scheduled task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            Success message
        """
        if task_id not in self.scheduled_tasks:
            return f"Task with ID {task_id} not found"
            
        # Remove from scheduled tasks
        task_name = self.scheduled_tasks[task_id]["name"]
        self.scheduled_tasks.pop(task_id, None)
        
        # Save scheduled tasks to memory
        self._save_scheduled_tasks()
        
        return f"Task '{task_name}' cancelled successfully"
    
    def create_script(self, script_name, script_content):
        """
        Create a new automation script.
        
        Args:
            script_name: Name of the script
            script_content: Content of the script
            
        Returns:
            Success message
        """
        try:
            # Ensure scripts directory exists
            scripts_dir = self.automation_settings.get("scripts_directory")
            if not os.path.exists(scripts_dir):
                os.makedirs(scripts_dir)
                
            # Create script file
            script_path = os.path.join(scripts_dir, f"{script_name}.py")
            with open(script_path, "w") as f:
                f.write(script_content)
                
            return f"Script '{script_name}' created successfully"
        except Exception as e:
            self.logger.error(f"Error creating script: {str(e)}")
            return f"Failed to create script. Error: {str(e)}"
    
    def run_script(self, script_name, args=None):
        """
        Run an automation script.
        
        Args:
            script_name: Name of the script to run
            args: Arguments to pass to the script
            
        Returns:
            Script output
        """
        try:
            # Get script path
            scripts_dir = self.automation_settings.get("scripts_directory")
            script_path = os.path.join(scripts_dir, f"{script_name}.py")
            
            if not os.path.exists(script_path):
                return f"Script '{script_name}' not found"
                
            # Build command
            cmd = ["python", script_path]
            if args:
                if isinstance(args, list):
                    cmd.extend(args)
                else:
                    cmd.append(str(args))
                    
            # Run script
            result = self.system_control.execute_command(" ".join(cmd))
            return result
        except Exception as e:
            self.logger.error(f"Error running script: {str(e)}")
            return f"Failed to run script. Error: {str(e)}"
    
    def list_scripts(self):
        """
        List all available automation scripts.
        
        Returns:
            List of script names
        """
        try:
            scripts_dir = self.automation_settings.get("scripts_directory")
            if not os.path.exists(scripts_dir):
                return []
                
            scripts = []
            for file in os.listdir(scripts_dir):
                if file.endswith(".py"):
                    scripts.append(file[:-3])  # Remove .py extension
                    
            return scripts
        except Exception as e:
            self.logger.error(f"Error listing scripts: {str(e)}")
            return []
    
    def delete_script(self, script_name):
        """
        Delete an automation script.
        
        Args:
            script_name: Name of the script to delete
            
        Returns:
            Success message
        """
        try:
            scripts_dir = self.automation_settings.get("scripts_directory")
            script_path = os.path.join(scripts_dir, f"{script_name}.py")
            
            if not os.path.exists(script_path):
                return f"Script '{script_name}' not found"
                
            os.remove(script_path)
            return f"Script '{script_name}' deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting script: {str(e)}")
            return f"Failed to delete script. Error: {str(e)}"
    
    def create_workflow(self, name, steps):
        """
        Create an automation workflow with multiple steps.
        
        Args:
            name: Name of the workflow
            steps: List of workflow steps
            
        Returns:
            Success message
        """
        try:
            # Create workflow
            workflow = {
                "name": name,
                "steps": steps,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "status": "created"
            }
            
            # Save to memory
            workflows = self.memory_manager.get_preference("workflows") or {}
            workflows[name] = workflow
            self.memory_manager.store_preference("workflows", workflows)
            
            return f"Workflow '{name}' created successfully"
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            return f"Failed to create workflow. Error: {str(e)}"
    
    def run_workflow(self, workflow_name):
        """
        Run an automation workflow.
        
        Args:
            workflow_name: Name of the workflow to run
            
        Returns:
            Workflow results
        """
        try:
            # Get workflow
            workflows = self.memory_manager.get_preference("workflows") or {}
            if workflow_name not in workflows:
                return f"Workflow '{workflow_name}' not found"
                
            workflow = workflows[workflow_name]
            workflow["status"] = "running"
            workflow["last_run"] = datetime.now().isoformat()
            
            # Run each step
            results = []
            for step in workflow["steps"]:
                step_type = step.get("type")
                step_params = step.get("params", {})
                
                if step_type == "command":
                    result = self.system_control.execute_command(step_params.get("command"))
                elif step_type == "script":
                    result = self.run_script(step_params.get("script_name"), step_params.get("args"))
                else:
                    result = f"Unknown step type: {step_type}"
                    
                results.append(result)
                
                # Check for failure
                if "failed" in result.lower() or "error" in result.lower():
                    workflow["status"] = "failed"
                    break
                    
            # Update workflow status
            if workflow["status"] != "failed":
                workflow["status"] = "completed"
                
            workflow["results"] = results
            
            # Save to memory
            workflows[workflow_name] = workflow
            self.memory_manager.store_preference("workflows", workflows)
            
            return f"Workflow '{workflow_name}' executed with status: {workflow['status']}"
        except Exception as e:
            self.logger.error(f"Error running workflow: {str(e)}")
            return f"Failed to run workflow. Error: {str(e)}"
