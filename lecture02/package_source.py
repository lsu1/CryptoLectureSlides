"""Create a standalone editable source bundle; original uploads are excluded."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
R=Path(__file__).parent
NAMES=['README.md','CHANGES.md','requirements.txt','deck_schema.py','crypto_examples.py',
       'otp_content.py','block_content.py','des_content.py','slide_content.py','diagrams.py',
       'build_lecture.py','math_typesetting.py','build_guide.py','validate.py','package_source.py',
       'slide_manifest.json','worked_examples.json','session_plan.json','layout_checks.json','validation.json']
for name in NAMES:
 if not (R/name).is_file():raise FileNotFoundError(name)
with ZipFile(R/'Lecture02_Source.zip','w',ZIP_DEFLATED) as z:
 for name in NAMES:z.write(R/name,name)
print('Packaged',len(NAMES),'editable source and verification files.')
