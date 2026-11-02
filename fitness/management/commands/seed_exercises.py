from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fitness.models import Exercise, ExerciseMuscle, Muscle


EXERCISES_BATCH_1 = [
    {
        'name': 'Barbell Back Squat', 'movement_pattern': 'squat', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 4,
        'stability': 4, 'recovery_cost': 4, 'axial_load': 3, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 2, 'primary_muscles': ['quads', 'glutes'],
        'secondary_muscles': ['abs', 'lower_back'],
    },
    {
        'name': 'Leg Press', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 1, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': [],
    },
    {
        'name': 'Romanian Deadlift', 'movement_pattern': 'hinge', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 3, 'axial_load': 3, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 2, 'primary_muscles': ['hamstrings', 'glutes'],
        'secondary_muscles': ['lower_back'],
    },
    {
        'name': 'Conventional Deadlift', 'movement_pattern': 'hinge', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 2, 'skill_requirement': 4,
        'stability': 4, 'recovery_cost': 5, 'axial_load': 3, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 3, 'primary_muscles': ['glutes', 'hamstrings'],
        'secondary_muscles': ['lower_back', 'quads', 'traps', 'upper_back'],
    },
    {
        'name': 'Barbell Bench Press', 'movement_pattern': 'horizontal_push', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 3, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 2, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['triceps', 'front_delt'],
    },
    {
        'name': 'Incline Dumbbell Press', 'movement_pattern': 'horizontal_push', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 2, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['front_delt', 'triceps'],
    },
    {
        'name': 'Machine Chest Press', 'movement_pattern': 'horizontal_push', 'exercise_role': 'secondary',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['triceps', 'front_delt'],
    },
    {
        'name': 'Standing Barbell Overhead Press', 'movement_pattern': 'vertical_push', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 4,
        'stability': 4, 'recovery_cost': 3, 'axial_load': 2, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 3, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['front_delt'],
        'secondary_muscles': ['triceps', 'lateral_delt', 'abs'],
    },
    {
        'name': 'Seated Dumbbell Shoulder Press', 'movement_pattern': 'vertical_push', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 3, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['front_delt', 'lateral_delt'], 'secondary_muscles': ['triceps'],
    },
    {
        'name': 'Barbell Row', 'movement_pattern': 'horizontal_pull', 'exercise_role': 'primary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 3, 'axial_load': 3, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 2, 'primary_muscles': ['lats', 'upper_back'],
        'secondary_muscles': ['biceps', 'rear_delt', 'lower_back'],
    },
    {
        'name': 'Chest-Supported Dumbbell Row', 'movement_pattern': 'horizontal_pull', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['upper_back', 'lats'],
        'secondary_muscles': ['biceps', 'rear_delt'],
    },
    {
        'name': 'Seated Cable Row', 'movement_pattern': 'horizontal_pull', 'exercise_role': 'secondary',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['lats', 'upper_back'],
        'secondary_muscles': ['biceps', 'rear_delt'],
    },
    {
        'name': 'Lat Pulldown', 'movement_pattern': 'vertical_pull', 'exercise_role': 'secondary',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lats'], 'secondary_muscles': ['biceps', 'upper_back'],
    },
    {
        'name': 'Pull-Up', 'movement_pattern': 'vertical_pull', 'exercise_role': 'primary',
        'equipment': 'pull_up_bar', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'reps', 'joint_shoulder': 2, 'joint_elbow': 2, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lats'], 'secondary_muscles': ['biceps', 'upper_back'],
    },
    {
        'name': 'Bulgarian Split Squat', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'unilateral', 'sfr': 4, 'skill_requirement': 3,
        'stability': 4, 'recovery_cost': 3, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 1, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': ['hamstrings'],
    },
    {
        'name': 'Barbell Hip Thrust', 'movement_pattern': 'hinge', 'exercise_role': 'secondary',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 2, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 1, 'primary_muscles': ['glutes'], 'secondary_muscles': ['hamstrings'],
    },
    {
        'name': 'Leg Extension', 'movement_pattern': 'isolation_quads', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 0, 'primary_muscles': ['quads'], 'secondary_muscles': [],
    },
    {
        'name': 'Lying Leg Curl', 'movement_pattern': 'isolation_hamstrings', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 0, 'primary_muscles': ['hamstrings'], 'secondary_muscles': [],
    },
    {
        'name': 'Standing Calf Raise Machine', 'movement_pattern': 'isolation_calves', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['calves'], 'secondary_muscles': [],
    },
    {
        'name': 'Dumbbell Lateral Raise', 'movement_pattern': 'isolation_lateral_delt', 'exercise_role': 'accessory',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lateral_delt'], 'secondary_muscles': [],
    },
    {
        'name': 'Cable Lateral Raise', 'movement_pattern': 'isolation_lateral_delt', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'unilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lateral_delt'], 'secondary_muscles': [],
    },
    {
        'name': 'Cable Triceps Pushdown', 'movement_pattern': 'isolation_triceps', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['triceps'], 'secondary_muscles': [],
    },
    {
        'name': 'Overhead Cable Triceps Extension', 'movement_pattern': 'isolation_triceps', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['triceps'], 'secondary_muscles': [],
    },
    {
        'name': 'Incline Dumbbell Curl', 'movement_pattern': 'isolation_biceps', 'exercise_role': 'accessory',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['biceps'], 'secondary_muscles': [],
    },
    {
        'name': 'Cable Chest Fly', 'movement_pattern': 'isolation_chest', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['front_delt'],
    },
]


EXERCISES_BATCH_2 = [
    {
        'name': 'Goblet Squat', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 1, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': ['abs'],
    },
    {
        'name': 'Hack Squat Machine', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 1, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 1, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': [],
    },
    {
        'name': 'Smith Machine Squat', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'smith_machine', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 2,
        'stability': 2, 'recovery_cost': 3, 'axial_load': 3, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 2, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': ['lower_back'],
    },
    {
        'name': 'Dumbbell Walking Lunge', 'movement_pattern': 'squat', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'alternating', 'sfr': 3, 'skill_requirement': 2,
        'stability': 4, 'recovery_cost': 3, 'axial_load': 2, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 2,
        'joint_lower_back': 1, 'primary_muscles': ['quads', 'glutes'], 'secondary_muscles': ['hamstrings'],
    },
    {
        'name': 'Band Pull-Apart', 'movement_pattern': 'isolation_rear_delt', 'exercise_role': 'accessory',
        'equipment': 'resistance_band', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'band_tension', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['rear_delt'], 'secondary_muscles': ['upper_back'],
    },
    {
        'name': 'Dumbbell Romanian Deadlift', 'movement_pattern': 'hinge', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 1, 'primary_muscles': ['hamstrings', 'glutes'], 'secondary_muscles': ['lower_back'],
    },
    {
        'name': '45-Degree Back Extension', 'movement_pattern': 'hinge', 'exercise_role': 'secondary',
        'equipment': 'bodyweight', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'midrange',
        'loading_scheme': 'reps', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 2, 'primary_muscles': ['glutes', 'hamstrings'], 'secondary_muscles': ['lower_back'],
    },
    {
        'name': 'Seated Leg Curl', 'movement_pattern': 'isolation_hamstrings', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 0, 'primary_muscles': ['hamstrings'], 'secondary_muscles': [],
    },
    {
        'name': 'Seated Calf Raise', 'movement_pattern': 'isolation_calves', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['calves'], 'secondary_muscles': [],
    },
    {
        'name': 'Push-Up', 'movement_pattern': 'horizontal_push', 'exercise_role': 'secondary',
        'equipment': 'bodyweight', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'reps', 'joint_shoulder': 1, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['triceps', 'front_delt', 'abs'],
    },
    {
        'name': 'Chest Dips', 'movement_pattern': 'horizontal_push', 'exercise_role': 'secondary',
        'equipment': 'dip_bar', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'reps', 'joint_shoulder': 3, 'joint_elbow': 2, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest', 'triceps'], 'secondary_muscles': ['front_delt'],
    },
    {
        'name': 'Dumbbell Bench Press', 'movement_pattern': 'horizontal_push', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 2, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['chest'], 'secondary_muscles': ['triceps', 'front_delt'],
    },
    {
        'name': 'Kettlebell Swing', 'movement_pattern': 'hinge', 'exercise_role': 'secondary',
        'equipment': 'kettlebell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 1,
        'joint_lower_back': 2, 'primary_muscles': ['glutes', 'hamstrings'], 'secondary_muscles': ['lower_back', 'abs'],
    },
    {
        'name': "Dumbbell Farmer's Carry", 'movement_pattern': 'carry', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 1,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'midrange',
        'loading_scheme': 'time', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['traps'], 'secondary_muscles': ['abs', 'upper_back'],
    },
    {
        'name': 'Face Pull', 'movement_pattern': 'isolation_rear_delt', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['rear_delt'], 'secondary_muscles': ['upper_back'],
    },
    {
        'name': 'Reverse Pec Deck', 'movement_pattern': 'isolation_rear_delt', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 5, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['rear_delt'], 'secondary_muscles': ['upper_back'],
    },
    {
        'name': 'One-Arm Dumbbell Row', 'movement_pattern': 'horizontal_pull', 'exercise_role': 'secondary',
        'equipment': 'dumbbell', 'laterality': 'unilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 2, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['lats', 'upper_back'], 'secondary_muscles': ['biceps', 'rear_delt'],
    },
    {
        'name': 'TRX Row', 'movement_pattern': 'horizontal_pull', 'exercise_role': 'secondary',
        'equipment': 'trx', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 2,
        'stability': 3, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'reps', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['upper_back', 'lats'], 'secondary_muscles': ['biceps', 'rear_delt'],
    },
    {
        'name': 'Chin-Up', 'movement_pattern': 'vertical_pull', 'exercise_role': 'secondary',
        'equipment': 'pull_up_bar', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 3,
        'stability': 3, 'recovery_cost': 2, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'reps', 'joint_shoulder': 1, 'joint_elbow': 3, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lats', 'biceps'], 'secondary_muscles': ['upper_back'],
    },
    {
        'name': 'Straight-Arm Cable Pulldown', 'movement_pattern': 'isolation_lats', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['lats'], 'secondary_muscles': [],
    },
    {
        'name': 'Dumbbell Shrug', 'movement_pattern': 'isolation_traps', 'exercise_role': 'accessory',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 3, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['traps'], 'secondary_muscles': [],
    },
    {
        'name': 'Hammer Curl', 'movement_pattern': 'isolation_biceps', 'exercise_role': 'accessory',
        'equipment': 'dumbbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'midrange',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['biceps'], 'secondary_muscles': [],
    },
    {
        'name': 'Machine Preacher Curl', 'movement_pattern': 'isolation_biceps', 'exercise_role': 'accessory',
        'equipment': 'machine', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 1, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 1, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['biceps'], 'secondary_muscles': [],
    },
    {
        'name': 'EZ-Bar Skull Crusher', 'movement_pattern': 'isolation_triceps', 'exercise_role': 'accessory',
        'equipment': 'barbell', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 2,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'stretched',
        'loading_scheme': 'weight', 'joint_shoulder': 1, 'joint_elbow': 2, 'joint_knee': 0,
        'joint_lower_back': 0, 'primary_muscles': ['triceps'], 'secondary_muscles': [],
    },
    {
        'name': 'Cable Crunch', 'movement_pattern': 'isolation_abs', 'exercise_role': 'accessory',
        'equipment': 'cable', 'laterality': 'bilateral', 'sfr': 4, 'skill_requirement': 1,
        'stability': 2, 'recovery_cost': 1, 'axial_load': 1, 'length_bias': 'shortened',
        'loading_scheme': 'weight', 'joint_shoulder': 0, 'joint_elbow': 0, 'joint_knee': 0,
        'joint_lower_back': 1, 'primary_muscles': ['abs'], 'secondary_muscles': [],
    },
]


EXERCISE_FIELDS = (
    'movement_pattern', 'exercise_role', 'equipment', 'laterality', 'sfr',
    'skill_requirement', 'stability', 'recovery_cost', 'axial_load', 'length_bias',
    'loading_scheme', 'joint_shoulder', 'joint_elbow', 'joint_knee', 'joint_lower_back',
)


def exercise_batches():
    return [
        batch
        for name, batch in sorted(globals().items())
        if name.startswith('EXERCISES_BATCH_')
    ]


class Command(BaseCommand):
    help = 'Seed exercises and their muscle relationships.'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for batch in exercise_batches():
                for exercise_data in batch:
                    muscle_names = exercise_data['primary_muscles'] + exercise_data['secondary_muscles']
                    muscles = {}
                    for muscle_name in muscle_names:
                        try:
                            muscles[muscle_name] = Muscle.objects.get(name=muscle_name)
                        except Muscle.DoesNotExist as exc:
                            raise CommandError(
                                f'Muscle "{muscle_name}" does not exist. Run seed_muscles first.'
                            ) from exc

                    defaults = {
                        field: exercise_data[field]
                        for field in EXERCISE_FIELDS
                    }
                    exercise, created = Exercise.objects.update_or_create(
                        name=exercise_data['name'],
                        defaults=defaults,
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    for muscle_name in exercise_data['primary_muscles']:
                        ExerciseMuscle.objects.update_or_create(
                            exercise=exercise,
                            muscle=muscles[muscle_name],
                            defaults={'is_primary': True},
                        )
                    for muscle_name in exercise_data['secondary_muscles']:
                        ExerciseMuscle.objects.update_or_create(
                            exercise=exercise,
                            muscle=muscles[muscle_name],
                            defaults={'is_primary': False},
                        )

        total_count = Exercise.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Exercises created: {created_count}; updated: {updated_count}; '
                f'total: {total_count}.'
            )
        )