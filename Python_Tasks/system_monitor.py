"""
When executed, it should collect your System's CPU utilization,

Free space, and other vitals and display it in a good format on the screen.
The same has to be written to a file and
 every execution of the script should append the details
Set some threshold values of each of the vitals
(configurable inside a separate config file)
such that once they go beyond, you send out an email
"""


#import os
import smtplib
import configparser
from email.mime.text import MIMEText
import psutil


class SystemMonitor:
    """
    class SystemMonitor is used to monitize system
    """
    def __init__(self):
        """
        This method for intilize configuration
        """
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.thresholds = {
            'cpu_percent': float(self.config.get('thresholds', 'cpu_percent')),
            'disk_percent': float(self.config.get('thresholds', 'disk_percent')),
            'mem_percent': float(self.config.get('thresholds', 'mem_percent'))
        }

    def collect_system_info(self):
        """
        This method for collect system information
        """
        cpu_percent = psutil.cpu_percent()
        disk_percent = psutil.disk_usage('/').percent
        mem_percent = psutil.virtual_memory().percent
        free_space = psutil.disk_usage('/').free

        return {
            'cpu_percent': cpu_percent,
            'disk_percent': disk_percent,
            'mem_percent': mem_percent,
            'free_space': free_space
        }

    def write_to_file(self, data):
        """
         This is used to write to file
         """
        with open('system_info.txt', 'a') as file:
            file.write(f"{data['cpu_percent']}, {data['disk_percent']},"
                       f" {data['mem_percent']}, {data['free_space']}\n")

    def send_email(self, subject, message):
        """
        this method for intilize the emails
        """
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = self.config.get('email', 'from')
        msg['To'] = self.config.get('email', 'to')

        s = smtplib.SMTP(self.config.get('email', 'smtp_server'))
        s.starttls()
        s.login(self.config.get('email', 'username'), self.config.get('email', 'password'))
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

    def check_thresholds(self, data):
        """
        This method check threshold system
        """
        if data['cpu_percent'] > self.thresholds['cpu_percent']:
            self.send_email('CPU usage threshold exceeded', f"CPU usage: {data['cpu_percent']}")

        if data['disk_percent'] > self.thresholds['disk_percent']:
            self.send_email('Disk usage threshold exceeded', f"Disk usage: {data['disk_percent']}")

        if data['mem_percent'] > self.thresholds['mem_percent']:
            self.send_email('Memory usage threshold exceeded', f"Memory usage: {data['mem_percent']}")

    def run(self):
        """
        This method for run script
        """
        system_info = self.collect_system_info()
        self.write_to_file(system_info)
        self.check_thresholds(system_info)
