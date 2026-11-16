from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from docx import Document
import hashlib, json

ROOT=Path(__file__).parent
SOURCE=Path(r'C:\Users\lb119\Downloads\GDD (1).docx')
TEMPLATE=Path(r'C:\Users\lb119\.codex\skills\artifact-template-gdd\assets\reference.docx')
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
inventory={}
with ZipFile(SOURCE) as z:
    for f in z.infolist():
        b=z.read(f.filename)
        inventory[f.filename]={'size':len(b),'sha256':hashlib.sha256(b).hexdigest()}
        if f.filename.startswith('word/media/'):
            p=ROOT/'source-media'/Path(f.filename).name
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(b)
    st=etree.fromstring(z.read('word/styles.xml'))
    defaults=st.find('w:docDefaults',NS)
    print('DEFAULTS',etree.tostring(defaults).decode())
    root=etree.fromstring(z.read('word/document.xml'))
    print('SPECIAL', {k:len(root.findall('.//w:'+k,NS)) for k in ['sdt','txbxContent','fldChar','sectPr']})
    print('PICTURES',[(i,p.xpath('.//a:blip/@r:embed',namespaces={**NS,'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'})) for i,p in enumerate(root.findall('w:body/w:p',NS)) if p.find('.//a:blip',NS) is not None])
    print('RELS',z.read('word/_rels/document.xml.rels').decode())
d=Document(SOURCE)
lines=[]
for i,e in enumerate(d.element.body):
    lines.append(f'{i} {etree.QName(e).localname} '+ ' | '.join(e.xpath('.//w:t/text()')))
(ROOT/'source-outline.txt').write_text('\n'.join(lines),encoding='utf-8')
(ROOT/'source-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print('TABLES',[(i,len(t.rows),len(t.columns)) for i,t in enumerate(d.tables)])
print('BODY_P0',d.paragraphs[2]._p.xml)
print('CELL0',d.tables[0].cell(0,0)._tc.xml)
print('TEMPLATE_SAME',SOURCE.read_bytes()==TEMPLATE.read_bytes())
