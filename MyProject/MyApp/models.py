from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('team_member', 'Team Member'),
        ('project_leader', 'Project Leader'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

def __str__(self):
        return self.username

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)  # Added due date
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0)  # Project progress in percentage

    def __str__(self):
        return self.name

    def calculate_progress(self):
        """Calculate the progress of the project as a percentage."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return (completed_tasks / total_tasks) * 100

    def save(self, *args, **kwargs):
        """Automatically update project progress before saving."""
        self.progress = self.calculate_progress()
        super().save(*args, **kwargs)

    def get_task_summary(self):
        """Return task details for a summary report."""
        tasks = self.tasks.all()
        return [
            {
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date,
                "progress": task.progress,
            }
            for task in tasks
        ]

ROLE_CHOICES = [
    ('team_member', 'Team Member'),
    ('project_manager', 'Project Manager'),
]

class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    due_date = models.DateField(null=True, blank=True)  # Added due date
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='team_member')
    joined_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0)  # Project progress in percentage

    def __str__(self):
        return f"{self.user.username} in {self.project.name}"

    @staticmethod
    def get_projects_by_leader(user):
        """Retrieve all projects led by a specific project leader."""
        return Project.objects.filter(members__user=user, members__role='project_manager')

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress = models.FloatField(default=0)  # Task progress in percentage (0-100)

    def __str__(self):
        return f"{self.name} ({self.status})"

    @staticmethod
    def get_user_tasks(user):
        """Retrieve all tasks assigned to a specific user."""
        return Task.objects.filter(assigned_to=user)

    def save(self, *args, **kwargs):
        """Ensure the parent project’s progress is updated when a task is saved."""
        super().save(*args, **kwargs)
        if self.project:
            self.project.save()  # Update the project's progress whenever a task is saved

    def update_task_status(self, status):
        """Update the status of the task and ensure the project's progress is recalculated."""
        self.status = status
        self.save()  # This will automatically update the project progress due to the overridden save method in Task