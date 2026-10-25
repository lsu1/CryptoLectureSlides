"""MH6003 course-information draft: course outline, screenshot, and user clarifications."""
COURSE=dict(code='MH6003',title='Cryptography',academic_units=3,academic_year='2026–2027',session='6:30–10:00 pm')
INSTRUCTORS=[dict(name='Prof. Wang Huaxiong',email='HXWang@ntu.edu.sg'),dict(name='Dr. Su Le',email='LSU1@e.ntu.edu.sg')]
WEEKS=[
 (1,'Basic concepts of cryptography and its applications'),
 (2,'Symmetric-key cryptography: block ciphers and stream ciphers'),
 (3,'Symmetric-key cryptography: block ciphers and stream ciphers'),
 (4,'Cryptographic hash functions and message authentication codes'),
 (5,'Cryptographic hash functions and message authentication codes'),
 (6,'Public-key cryptography: encryption and signatures'),
 (7,'Public-key cryptography: encryption and signatures; mid-term test'),
 (8,'Public-key cryptography: encryption and signatures'),
 (9,'Pseudorandom number generation'),
 (10,'Identification schemes and entity authentication'),
 (11,'Key distribution and key agreement schemes'),
 (12,'Key distribution/agreement and public-key infrastructure (PKI)'),
 (13,'Revision (about 1 hour), followed by the final exam (2 hours)'),
]
ASSESSMENTS=[
 dict(id='midterm',title='Mid-term test',weight=20,mode='Individual',week=7,hours=1,format='Closed book'),
 dict(id='project',title='Group project',weight=30,mode='Team',members_min=3,members_max=4,start_week=8,end_week=11),
 dict(id='final',title='Final examination',weight=50,mode='Individual',week=13,hours=2,format='Closed book'),
]
PROJECT=dict(group_size='3–4 students',topic_by_week=7,start_week=8,end_week=11,duration_weeks=4,submission='By the end of week 11',contributions='State each member’s individual contribution.')
SLIDES=[
 dict(id='cover',title='Cryptography',kicker='MH6003',subtitle='Course information'),
 dict(id='instructors',title='Your instructors',kicker='CONTACT'),
 dict(id='weeks_first',title='Weekly topics / weeks 1–6',kicker='COURSE SCHEDULE'),
 dict(id='weeks_second',title='Weekly topics / weeks 7–13',kicker='COURSE SCHEDULE'),
 dict(id='grading',title='How the course is graded',kicker='ASSESSMENT'),
 dict(id='exams',title='Exam arrangements',kicker='MID-TERM AND FINAL'),
 dict(id='project',title='Group project / plan ahead',kicker='TEAMWORK'),
]
SOURCES=[
 dict(id='outline',name='OBTL MH6003.docx',role='Course identity, instructor names/emails, weekly topics, assessment weights, and contribution declaration.',status='Uploaded document inspected; original not redistributed.'),
 dict(id='screenshot',name='User-provided grading discussion screenshot',role='One-hour mid-term, two-hour final, both closed book; teams of 3–4; group/topic selection by week 7; project weeks 8–11; submission by end of week 11.',status='Arrangements transcribed without email headers, recipients, or unrelated correspondence.'),
 dict(id='clarification',name='User clarification in this conversation',role='List both instructors. Week 12 remains regular teaching. Week 13 has about one hour of revision followed by a two-hour final.',status='Takes precedence over the screenshot’s suggestion to reserve weeks 12–13 for review.'),
 dict(id='session',name='Earlier user instruction in this conversation',role='Evening session runs from 6:30 to 10:00 pm.',status='No weekday, venue, calendar dates, or exam clock times were supplied.'),
]
