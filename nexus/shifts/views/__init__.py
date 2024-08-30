COLOR_CODE = {
    "SI Session": "#FF4500",
    "Group Tutoring": "#FFA500",
    "Tutor Drop-In": "#4169E1",
    "Tutor Appointment": "#6A5ACD",
    "OURS Mentor Hours": "#FFD700",
    "OA Hours": "#FF69B4",
    "Training": "#8B0000",
    "Meeting": "#B22222",
    "Class": "#DC143C",
    "Observation": "#008080",
    "Preparation": "#7FFFD4",
    "Other": "#000000",
}

def color_coder(shift_kind):
	if shift_kind not in COLOR_CODE:
		return "black"
	return COLOR_CODE[shift_kind]

def get_color_coder_dict():
	return COLOR_CODE