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
        # Use prefetched data if available, otherwise query
        if hasattr(self, '_prefetched_objects_cache') and 'assigned_courses' in self._prefetched_objects_cache:
            courses = self._prefetched_objects_cache['assigned_courses']
        else:
            courses = self.assigned_courses.all()
        return f"[{', '.join([str(course) for course in courses])}]"
    
    def __str__(self):
        return f"{self.position.user.first_name} - {self.str_assigned_courses()}"