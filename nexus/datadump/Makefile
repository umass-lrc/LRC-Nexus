create_dump:
	@echo "Creating data dump..."
	@python ../manage.py dumpdata auth.Group core.Semester core.Holiday core.DaySwitch core.CourseSubject core.Course core.Faculty core.Buildings core.Classes core.ClassTimes users.NexusUser users.Positions users.PositionGroups shifts.RecurringShift shifts.Shift shifts.AttendanceInfo shifts.ChangeRequest shifts.DropRequest payrolls.Payroll payrolls.PayrollInHR payrolls.PayrollInHRViaLatePay payrolls.PayrollNotInHR payrolls.PayrollNotSigned SIs.SIRoleInfo SIs.SIReccuringShiftInfo tutors.TutorRoleInfo ours.Keyword ours.FacultyPosition ours.FacultyDetails ours.Majors ours.Tracks ours.CitizenshipStatus ours.Opportunity ours.MinGPARestriction ours.MajorRestriction ours.CitizenshipRestriction ours.StudyLevel ours.StudyLevelRestriction ours.CustomOpportunityRestrictions > data_dump.json

load_dump:
	@echo "Loading data dump..."
	@python load_data.py