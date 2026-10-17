"""
Seeds Diamond Learning with realistic sample data so the app is testable
immediately: all three education levels, every subject on the official BEC
subject lists, a handful of subjects fleshed out with topics/notes/papers/
questions, and a demo student account.

Run with:  python manage.py seed_data
Safe to re-run — uses get_or_create throughout.
"""
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile
from apps.notes.models import Note
from apps.papers.models import PastPaper, SolvedQuestion, TopicalQuestion
from apps.syllabus.models import EducationLevel, Subject, Topic, Subtopic

LEVELS = {
    "PSLE": {
        "name": "Primary School Leaving Examination",
        "description": "The foundation stage exam at the end of primary school, testing core literacy, numeracy and general knowledge before students move on to junior secondary.",
        "order": 1,
        "subjects": ["Mathematics", "English", "Science", "Setswana", "Social Studies", "Agriculture", "Religious & Moral Education"],
    },
    "JCE": {
        "name": "Junior Certificate Examination",
        "description": "The exam at the end of junior secondary school. Builds on the PSLE foundation and widens into electives ahead of BGCSE.",
        "order": 2,
        "subjects": ["Mathematics", "English", "Science", "Setswana", "Social Studies", "Agriculture", "Design and Technology",
                     "Moral Education", "Home Economics", "Commerce and Office Procedures", "Commerce and Accounting",
                     "Religious Education", "French", "Art", "Music", "Physical Education", "General Science"],
    },
    "BGCSE": {
        "name": "Botswana General Certificate of Secondary Education",
        "description": "The senior certificate examined at the end of secondary school — the widest subject spread of the three levels.",
        "order": 3,
        "subjects": ["Mathematics", "English Language", "Science (Single Award)", "Science (Double Award)", "Chemistry", "Physics",
                     "Biology", "Human and Social Biology", "Setswana", "Additional Mathematics", "Statistics", "History",
                     "Geography", "Social Studies", "Development Studies", "Literature in English", "Religious Education",
                     "Design and Technology", "Art & Design", "Computer Studies", "Commerce", "Agriculture", "Food & Nutrition",
                     "Fashion & Fabrics", "Home Management", "Accounting", "Business Studies", "Physical Education", "Music",
                     "French", "Hospitality and Tourism Studies", "Animal Production", "Field Crop Production", "Horticulture"],
    },
}

# Compulsory subjects per level. Everything else on a level's list is optional
# and picked by the student at sign-up. PSLE has no choice: every subject is
# compulsory. Edit these lists to change which subjects students are asked to
# choose. seed_data runs on every deploy, so the lists here are the source of
# truth (an "Is core" change made only in /admin/ would be reset).
CORE_SUBJECTS = {
    "PSLE": None,  # None = every PSLE subject is compulsory
    "JCE": ["Mathematics", "English", "Science", "Setswana", "Social Studies", "Agriculture", "Moral Education"],
    "BGCSE": ["Mathematics", "English Language", "Setswana"],
}

# Subjects to flesh out fully with topics/notes/papers/questions (kept to a
# manageable demo set rather than all ~57 subject/level combinations).
DETAILED_SUBJECTS = {
    ("BGCSE", "Mathematics"): {
        "topics": [
            ("Algebra", "Manipulating expressions, solving equations and inequalities.",
             ["Simplify algebraic expressions", "Solve linear and quadratic equations", "Solve simultaneous equations"]),
            ("Geometry", "Properties of shapes, angles, and geometric proof.",
             ["Calculate angles in polygons", "Apply circle theorems", "Use Pythagoras' theorem"]),
            ("Trigonometry", "Relationships between angles and sides of triangles.",
             ["Use sine, cosine and tangent ratios", "Solve non-right-angled triangles", "Apply trigonometry to real-world problems"]),
            ("Statistics", "Collecting, representing, and interpreting data.",
             ["Calculate mean, median and mode", "Draw and interpret cumulative frequency graphs", "Calculate standard deviation"]),
        ],
        "paper_numbers": ["Paper 1", "Paper 2", "Paper 3"],
    },
    ("BGCSE", "English Language"): {
        "topics": [
            ("Comprehension", "Reading closely and answering questions on unseen passages.",
             ["Identify main ideas and supporting detail", "Infer meaning from context", "Summarise a passage concisely"]),
            ("Composition Writing", "Producing structured, well-argued essays.",
             ["Plan a five-paragraph essay", "Use varied sentence structures", "Write persuasively and descriptively"]),
            ("Summary Writing", "Condensing a text while preserving its key points.",
             ["Select relevant points only", "Write within a word limit", "Use own words rather than copying"]),
        ],
        "paper_numbers": ["Paper 1", "Paper 2"],
    },
    ("BGCSE", "Physics"): {
        "topics": [
            ("Mechanics", "Forces, motion, and energy.",
             ["Apply Newton's laws of motion", "Calculate work, energy and power", "Analyse motion graphs"]),
            ("Electricity", "Circuits, current, and electrical energy.",
             ["Apply Ohm's law", "Analyse series and parallel circuits", "Calculate electrical power and energy"]),
            ("Waves", "Properties and
