import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
from .config import settings
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.enabled = settings.smtp_enabled and settings.smtp_user and settings.smtp_password
        
    def send_task_notification(self, to_email: str, task_title: str, due_date: str, task_id: int) -> bool:
        """Send email notification for task deadline"""
        if not self.enabled:
            logger.warning("Email notifications are disabled")
            return False
        
        subject = f"🔔 Task Reminder: {task_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .button {{ background: #667eea; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; }}
                .urgent {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📋 Task Manager</h2>
                </div>
                <div class="content">
                    <h3>Task Deadline Reminder</h3>
                    <p>Hello!</p>
                    <p>This is an automated reminder about your task:</p>
                    <ul>
                        <li><strong>Task:</strong> {task_title}</li>
                        <li><strong>Due Date:</strong> {due_date}</li>
                    </ul>
                    <p>Please update the task status in the system.</p>
                    <a href="http://localhost:8501?task={task_id}" class="button">View Task</a>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply.</p>
                    <p>Task Manager System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['From'] = settings.smtp_from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_body, 'html'))
        
        try:
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            logger.info(f"Notification sent to {to_email} for task: {task_title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

notifier = EmailNotifier()