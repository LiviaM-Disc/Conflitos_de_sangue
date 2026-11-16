"""Use canonical DOCX rasterizer with an explicitly exported Microsoft Word PDF.

The bundled Windows runtime has no LibreOffice. The read-only Word export
replaces only the conversion step; the skill's rasterizer is used unchanged.
"""
import sys, os, importlib.util
from pathlib import Path
from pypdf import PdfReader
SKILL=Path(r'C:\Users\lb119\.codex\plugins\cache\openai-primary-runtime\documents\26.1112.11217\skills\documents')
POPPLER=Path(r'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt\dependencies\native\poppler\Library\bin')
os.environ['PATH']=str(POPPLER)+os.pathsep+os.environ.get('PATH','')
spec=importlib.util.spec_from_file_location('docx_renderer',SKILL/'render_docx.py')
renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
docx,pdf,out=map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert docx.exists() and pdf.exists()
renderer.convert_to_pdf=lambda *args,**kwargs:(str(pdf),'Microsoft Word read-only export; LibreOffice unavailable in Windows runtime.')
pages=renderer.rasterize(str(docx),str(out),120,False,False)
reader=PdfReader(str(pdf))
for i,page in enumerate(reader.pages):
    txt=page.extract_text()
    print(i+1,len(txt),txt[:100].replace('\n',' | '), 'END:',txt[-90:].replace('\n',' | '))
(out/'text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+p.extract_text() for i,p in enumerate(reader.pages)),encoding='utf-8')
print('RENDERED',len(pages))
