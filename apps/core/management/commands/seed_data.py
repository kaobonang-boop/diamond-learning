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
            ("Waves", "Properties and behaviour of waves.",
             ["Distinguish transverse and longitudinal waves", "Calculate wave speed, frequency and wavelength", "Explain reflection and refraction"]),
        ],
        "paper_numbers": ["Paper 1 (Multiple Choice)", "Paper 3 (Theory)", "Paper 5 (Alt. to Practical)"],
    },
    ("JCE", "Mathematics"): {
        "topics": [
            ("Number", "Working confidently with all number types.",
             ["Perform operations with fractions and decimals", "Understand ratio and proportion", "Calculate percentages"]),
            ("Algebra", "Introduction to algebraic manipulation.",
             ["Simplify expressions", "Solve linear equations", "Substitute into formulae"]),
            ("Geometry and Measurement", "Shapes, area, volume, and angles.",
             ["Calculate area and perimeter", "Calculate volume of solids", "Find missing angles"]),
        ],
        "paper_numbers": ["Paper 1", "Paper 2"],
    },
    ("JCE", "English"): {
        "topics": [
            ("Grammar and Usage", "Correct and effective use of English.",
             ["Use correct tense and agreement", "Apply punctuation rules", "Avoid common errors"]),
            ("Composition", "Writing for different purposes and audiences.",
             ["Write a narrative composition", "Write a formal letter", "Structure paragraphs clearly"]),
        ],
        "paper_numbers": ["Paper 1", "Paper 2", "Paper 3", "Paper 4"],
    },
    ("PSLE", "Mathematics"): {
        "topics": [
            ("Whole Numbers", "Place value, the four operations, and word problems.",
             ["Add and subtract large numbers", "Multiply and divide with regrouping", "Solve word problems"]),
            ("Fractions and Decimals", "Understanding and operating on parts of a whole.",
             ["Compare and order fractions", "Convert between fractions and decimals", "Add and subtract fractions"]),
            ("Shapes and Space", "Recognising and measuring 2D and 3D shapes.",
             ["Identify properties of 2D shapes", "Calculate area and perimeter", "Recognise 3D shapes and their nets"]),
        ],
        "paper_numbers": ["Paper 1"],
    },
    ("PSLE", "English"): {
        "topics": [
            ("Reading Comprehension", "Understanding and responding to short passages.",
             ["Answer literal and inferential questions", "Identify the main idea", "Build vocabulary from context"]),
            ("Composition Writing", "Writing simple narrative and descriptive pieces.",
             ["Write a clear beginning, middle and end", "Use descriptive language", "Check spelling and punctuation"]),
        ],
        "paper_numbers": ["Paper 1", "Paper 2"],
    },
}

NOTE_PARAGRAPHS = [
    "This note walks through {topic} step by step, the way it's usually examined at {level} level. Read it once for the overview, then come back to the worked examples when you're practising.",
    "Start by making sure you understand the key definitions — most marks are lost in exams not because students can't do the method, but because they misread what's actually being asked.",
    "Worked example: work through a typical exam-style question slowly, writing out every step, including the ones that feel obvious. Examiners give marks for method, not just the final answer.",
    "Common mistakes students make on this topic include rushing the setup, skipping units, and not checking whether the final answer is realistic. Build the habit of a quick sanity check.",
    "Before you move on, try the related questions in Topical Papers for this topic, then check your working against the Solved Papers for past exam versions of the same idea.",
]


class Command(BaseCommand):
    help = "Seed Diamond Learning with realistic PSLE/JCE/BGCSE demo data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding education levels and subjects…")
        level_objs = {}
        for code, info in LEVELS.items():
            level, _ = EducationLevel.objects.update_or_create(
                code=code, defaults={"name": info["name"], "description": info["description"], "order": info["order"]}
            )
            level_objs[code] = level
            for name in info["subjects"]:
                Subject.objects.get_or_create(education_level=level, name=name)

        self.stdout.write("Seeding topics, notes, papers and questions for the demo subject set…")
        for (level_code, subject_name), detail in DETAILED_SUBJECTS.items():
            level = level_objs[level_code]
            subject = Subject.objects.get(education_level=level, name=subject_name)

            for order, (title, description, objectives) in enumerate(detail["topics"]):
                topic, _ = Topic.objects.get_or_create(
                    subject=subject, title=title,
                    defaults={"description": description, "learning_objectives": "\n".join(objectives), "order": order},
                )
                Subtopic.objects.get_or_create(topic=topic, title=f"{title} — Worked Examples", defaults={"order": 1})
                Subtopic.objects.get_or_create(topic=topic, title=f"{title} — Common Exam Questions", defaults={"order": 2})

                # Note
                content = "\n\n".join(p.format(topic=title, level=level_code) for p in NOTE_PARAGRAPHS)
                Note.objects.get_or_create(
                    topic=topic, title=f"{title} — Study Notes",
                    defaults={"content": content},
                )

                # Topical (MCQ) questions
                for i in range(1, 6):
                    TopicalQuestion.objects.get_or_create(
                        topic=topic, order=i,
                        defaults={
                            "question_text": f"Sample {title} question {i}: which option correctly applies the method covered in this topic?",
                            "option_a": "Option A — a plausible but incorrect approach",
                            "option_b": "Option B — the correct method applied fully",
                            "option_c": "Option C — a common miscalculation",
                            "option_d": "Option D — an irrelevant distractor",
                            "correct_option": "B",
                            "explanation": f"Option B is correct because it applies the {title.lower()} method exactly as covered in the notes for this topic.",
                        },
                    )

                # Solved question tied to this topic
                SolvedQuestion.objects.get_or_create(
                    subject=subject, topic=topic, year=2025, paper_number=detail["paper_numbers"][0], question_number="1",
                    defaults={
                        "question_text": f"A typical {level_code} exam question on {title}.",
                        "step_by_step_explanation": f"Step 1: identify what's being asked. Step 2: apply the {title.lower()} method from the syllabus. Step 3: check the answer makes sense.",
                        "final_answer": "See the worked steps above for the final answer and units.",
                    },
                )

            # Past papers: last 3 years per paper number, left unattached (no file)
            # except one demo PDF so the download flow can be tested end to end.
            demo_pdf = None
            for paper_number in detail["paper_numbers"]:
                for year in (2023, 2024, 2025):
                    paper, created = PastPaper.objects.get_or_create(subject=subject, year=year, paper_number=paper_number)
                    if created and demo_pdf is None and year == 2025 and paper_number == detail["paper_numbers"][0]:
                        pdf_bytes = (
                            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
                            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
                            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 150]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
                            b"4 0 obj<</Length 90>>stream\nBT /F1 14 Tf 20 100 Td "
                            b"(Diamond Learning - Sample Past Paper) Tj ET\nendstream endobj\n"
                            b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
                            b"xref\n0 6\ntrailer<</Size 6/Root 1 0 R>>\n%%EOF"
                        )
                        paper.file.save(f"{subject.slug}-{paper_number.replace(' ', '_')}-{year}.pdf", ContentFile(pdf_bytes), save=True)

        self.stdout.write("Seeding a demo student account (username: student / password: diamond2026)…")
        if not User.objects.filter(username="student").exists():
            demo = User.objects.create_user(
                username="student", email="student@example.com", password="diamond2026",
                first_name="Kabelo", last_name="Mokgosi",
            )
            profile, _ = UserProfile.objects.get_or_create(user=demo)
            profile.education_level = level_objs["BGCSE"]
            profile.save()
            profile.subjects.set(Subject.objects.filter(
                education_level=level_objs["BGCSE"], name__in=["Mathematics", "English Language", "Physics"]
            ))

        self.stdout.write(self.style.SUCCESS("Seed data loaded."))
