from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Equipment(models.TextChoices):
    BARBELL = 'barbell', 'Barbell'
    DUMBBELL = 'dumbbell', 'Dumbbell'
    CABLE = 'cable', 'Cable'
    MACHINE = 'machine', 'Machine'
    SMITH_MACHINE = 'smith_machine', 'Smith machine'
    KETTLEBELL = 'kettlebell', 'Kettlebell'
    RESISTANCE_BAND = 'resistance_band', 'Resistance band'
    PULL_UP_BAR = 'pull_up_bar', 'Pull-up bar'
    DIP_BAR = 'dip_bar', 'Dip bar'
    TRX = 'trx', 'TRX'
    BODYWEIGHT = 'bodyweight', 'Bodyweight'


class Injury(models.TextChoices):
    SHOULDER = 'shoulder', 'Shoulder'
    ELBOW = 'elbow', 'Elbow'
    KNEE = 'knee', 'Knee'
    LOWER_BACK = 'lower_back', 'Lower back'


class AppUser(models.Model):
    class ExperienceLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'

    class Goal(models.TextChoices):
        MUSCLE_GAIN = 'muscle_gain', 'Muscle gain'
        STRENGTH = 'strength', 'Strength'

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    birth_year = models.IntegerField()
    height_cm = models.IntegerField()
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices)
    goal = models.CharField(max_length=20, choices=Goal.choices)
    available_equipment = models.JSONField(default=list)
    injuries = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username


class BodyWeightLog(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1)
    date = models.DateField()

    class Meta:
        db_table = 'body_weight_log'
        indexes = [models.Index(fields=['user', 'date'])]

    def __str__(self):
        return f'{self.user} - {self.date}: {self.weight_kg} kg'


class TrainingPlan(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    days_per_week = models.PositiveSmallIntegerField()
    mesocycle_weeks = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'training_plan'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_active=True),
                name='one_active_plan_per_user',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.name}'


class Workout(models.Model):
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    day_order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'workout'
        unique_together = [('plan', 'day_order')]

    def __str__(self):
        return f'{self.plan}: {self.name}'


class Muscle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    muscle_group = models.CharField(max_length=50)

    class Meta:
        db_table = 'muscle'

    def __str__(self):
        return self.name


class Exercise(models.Model):
    class MovementPattern(models.TextChoices):
        HORIZONTAL_PUSH = 'horizontal_push', 'Horizontal push'
        VERTICAL_PUSH = 'vertical_push', 'Vertical push'
        HORIZONTAL_PULL = 'horizontal_pull', 'Horizontal pull'
        VERTICAL_PULL = 'vertical_pull', 'Vertical pull'
        SQUAT = 'squat', 'Squat'
        HINGE = 'hinge', 'Hinge'
        CARRY = 'carry', 'Carry'
        ISOLATION_QUADS = 'isolation_quads', 'Isolation quads'
        ISOLATION_HAMSTRINGS = 'isolation_hamstrings', 'Isolation hamstrings'
        ISOLATION_CALVES = 'isolation_calves', 'Isolation calves'
        ISOLATION_LATERAL_DELT = 'isolation_lateral_delt', 'Isolation lateral delt'
        ISOLATION_REAR_DELT = 'isolation_rear_delt', 'Isolation rear delt'
        ISOLATION_CHEST = 'isolation_chest', 'Isolation chest'
        ISOLATION_ABS = 'isolation_abs', 'Isolation abs'
        ISOLATION_TRAPS = 'isolation_traps', 'Isolation traps'
        ISOLATION_LATS = 'isolation_lats', 'Isolation lats'
        ISOLATION_BICEPS = 'isolation_biceps', 'Isolation biceps'
        ISOLATION_TRICEPS = 'isolation_triceps', 'Isolation triceps'

    class ExerciseRole(models.TextChoices):
        PRIMARY = 'primary', 'Primary'
        SECONDARY = 'secondary', 'Secondary'
        ACCESSORY = 'accessory', 'Accessory'

    class Laterality(models.TextChoices):
        BILATERAL = 'bilateral', 'Bilateral'
        UNILATERAL = 'unilateral', 'Unilateral'
        ALTERNATING = 'alternating', 'Alternating'

    class LengthBias(models.TextChoices):
        STRETCHED = 'stretched', 'Stretched'
        MIDRANGE = 'midrange', 'Midrange'
        SHORTENED = 'shortened', 'Shortened'

    class LoadingScheme(models.TextChoices):
        WEIGHT = 'weight', 'Weight'
        REPS = 'reps', 'Reps'
        TIME = 'time', 'Time'
        BAND_TENSION = 'band_tension', 'Band tension'

    name = models.CharField(max_length=150, unique=True)
    movement_pattern = models.CharField(max_length=50, choices=MovementPattern.choices)
    exercise_role = models.CharField(max_length=20, choices=ExerciseRole.choices)
    equipment = models.CharField(max_length=20, choices=Equipment.choices)
    laterality = models.CharField(max_length=20, choices=Laterality.choices)
    sfr = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    skill_requirement = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    stability = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    recovery_cost = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    axial_load = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    length_bias = models.CharField(max_length=20, choices=LengthBias.choices)
    loading_scheme = models.CharField(max_length=20, choices=LoadingScheme.choices)
    joint_shoulder = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    joint_elbow = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    joint_knee = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    joint_lower_back = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])

    class Meta:
        db_table = 'exercise'
        constraints = [
            models.CheckConstraint(condition=Q(sfr__gte=1, sfr__lte=5), name='exercise_sfr_1_5'),
            models.CheckConstraint(condition=Q(skill_requirement__gte=1, skill_requirement__lte=5), name='exercise_skill_1_5'),
            models.CheckConstraint(condition=Q(stability__gte=1, stability__lte=5), name='exercise_stability_1_5'),
            models.CheckConstraint(condition=Q(recovery_cost__gte=1, recovery_cost__lte=5), name='exercise_recovery_1_5'),
            models.CheckConstraint(condition=Q(axial_load__gte=1, axial_load__lte=3), name='exercise_axial_load_1_3'),
            models.CheckConstraint(condition=Q(joint_shoulder__gte=0, joint_shoulder__lte=3), name='exercise_shoulder_0_3'),
            models.CheckConstraint(condition=Q(joint_elbow__gte=0, joint_elbow__lte=3), name='exercise_elbow_0_3'),
            models.CheckConstraint(condition=Q(joint_knee__gte=0, joint_knee__lte=3), name='exercise_knee_0_3'),
            models.CheckConstraint(condition=Q(joint_lower_back__gte=0, joint_lower_back__lte=3), name='exercise_lower_back_0_3'),
        ]

    def __str__(self):
        return self.name


class ExerciseMuscle(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    muscle = models.ForeignKey(Muscle, on_delete=models.CASCADE)
    is_primary = models.BooleanField()

    class Meta:
        db_table = 'exercise_muscle'
        unique_together = [('exercise', 'muscle')]

    def __str__(self):
        return f'{self.exercise} - {self.muscle}'


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField()
    target_sets = models.PositiveSmallIntegerField()
    rep_min = models.PositiveSmallIntegerField()
    rep_max = models.PositiveSmallIntegerField()
    target_rir = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(4)])
    rest_seconds = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'workout_exercise'
        unique_together = [('workout', 'position')]
        constraints = [
            models.CheckConstraint(condition=Q(target_rir__gte=0, target_rir__lte=4), name='workout_exercise_rir_0_4'),
        ]

    def __str__(self):
        return f'{self.workout} - {self.exercise}'


class WorkoutLog(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'workout_log'
        indexes = [models.Index(fields=['user', 'date'])]

    def __str__(self):
        return f'{self.user} - {self.date}'


class SetLog(models.Model):
    workout_log = models.ForeignKey(WorkoutLog, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    workout_exercise = models.ForeignKey(WorkoutExercise, null=True, blank=True, on_delete=models.SET_NULL)
    set_number = models.PositiveSmallIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveSmallIntegerField()
    rir = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(4)])

    class Meta:
        db_table = 'set_log'
        indexes = [models.Index(fields=['exercise', 'workout_log'])]
        constraints = [
            models.CheckConstraint(condition=Q(rir__isnull=True) | Q(rir__gte=0, rir__lte=4), name='set_log_rir_0_4'),
        ]

    def __str__(self):
        return f'{self.workout_log} - {self.exercise} set {self.set_number}'