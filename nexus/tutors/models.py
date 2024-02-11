from django.db import models

from shifts.models import (
    Shift,
)

from users.models import (
    Positions,
)

from core.models import (
    Course,
)

class TutorRoleInfo(models.Model):
    position = models.OneToOneField(
        to=Positions,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The position that this role is for."
    )
    
    assigned_courses = models.ManyToManyField(
        to=Course,
        help_text="Courses that this role is for."
    )
    
    def str_assigned_courses(self):
        return f"[{', '.join([str(course) for course in self.assigned_courses.all()])}]"